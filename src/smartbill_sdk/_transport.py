"""Shared transport logic for sync and async SmartBill clients.

The SmartBill API uses HTTP Basic Auth with ``username:token`` and returns
JSON envelopes whose root key depends on the endpoint (``sbcResponse``,
``Response``, ``sbcInvoicePaymentStatusResponse``, ``sbcSeries``,
``sbcTaxes``, ``stocks``). This module centralises request building, auth,
envelope unwrapping and error mapping so the sync and async clients stay DRY.
"""

from __future__ import annotations

import base64
import time
from typing import Any, Mapping, Optional, Union

import httpx

from .exceptions import (
    SmartBillAPIError,
    SmartBillAuthError,
    SmartBillRateLimitError,
    SmartBillTransportError,
)

DEFAULT_BASE_URL = "https://ws.smartbill.ro/SBORO/api/"
DEFAULT_TIMEOUT = 30.0

# Envelope root keys used by the SmartBill API responses.
_ENVELOPE_KEYS = (
    "sbcResponse",
    "Response",
    "sbcInvoicePaymentStatusResponse",
    "sbcSeries",
    "sbcTaxes",
    "stocks",
    "Fault",
)

# Fields that may carry an error message inside an envelope.
_ERROR_FIELDS = ("errorText", "errorTextError")


def build_auth_header(username: str, token: str) -> str:
    """Build the ``Authorization: Basic ...`` header value for ``username:token``."""
    raw = f"{username}:{token}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def build_auth(username: str, token: str) -> str:
    """Alias for :func:`build_auth_header` (kept for backwards-compat)."""
    return build_auth_header(username, token)


def build_request(
    *,
    method: str,
    base_url: str,
    path: str,
    params: Optional[Mapping[str, Any]] = None,
    json_body: Optional[Any] = None,
    accept: str = "application/json",
    content_type: str = "application/json",
    auth_header: Optional[str] = None,
) -> httpx.Request:
    """Construct an :class:`httpx.Request` with SmartBill default headers."""
    url = path if path.startswith("http") else base_url.rstrip("/") + "/" + path.lstrip("/")
    headers = {
        "Accept": accept,
        "Content-Type": content_type,
    }
    if auth_header:
        headers["Authorization"] = auth_header
    return httpx.Request(
        method.upper(),
        url,
        params=params,
        json=json_body,
        headers=headers,
    )


def parse_envelope(payload: Any) -> Any:
    """Unwrap the SmartBill response envelope and return its inner object.

    If the payload is a dict whose only key is one of the known envelope
    keys, the value under that key is returned. Otherwise the payload is
    returned unchanged (already unwrapped or a bare array/scalar).
    """
    if isinstance(payload, dict):
        if len(payload) == 1:
            (key, value), = payload.items()
            if key in _ENVELOPE_KEYS:
                return value
        # Some endpoints nest under an envelope but also include sibling
        # fields; pick the first known envelope key if present.
        for key in _ENVELOPE_KEYS:
            if key in payload:
                # Only unwrap when the envelope key is the "carrier".
                inner = payload[key]
                if isinstance(inner, dict):
                    return inner
    return payload


def _extract_error(envelope: Any) -> tuple[str, str]:
    if isinstance(envelope, dict):
        error_text = ""
        message = ""
        for f in _ERROR_FIELDS:
            v = envelope.get(f)
            if isinstance(v, str) and v.strip():
                error_text = v
                break
        m = envelope.get("message")
        if isinstance(m, str):
            message = m
        return error_text, message
    return "", ""


def handle_response(response: httpx.Response, *, binary: bool = False) -> Any:
    """Validate an :class:`httpx.Response` and return its parsed payload.

    Raises the appropriate :class:`SmartBillError` subclass for auth /
    rate-limit / API errors. When ``binary`` is true, the raw bytes are
    returned (used for PDF endpoints).
    """
    status = response.status_code

    if status == 401:
        raise SmartBillAuthError(
            f"Authentication failed (401). Check username/token and company CIF. "
            f"Body: {response.text[:200]}"
        )
    if status == 403:
        raise SmartBillRateLimitError(
            "Access blocked (403): rate limit exceeded. "
            "SmartBill blocks access for 10 minutes after >30 calls/10s."
        )

    if binary:
        if 200 <= status < 300:
            return response.content
        # Fall through to error handling below for non-2xx.

    if 200 <= status < 300:
        # PDF / octet-stream responses may have an empty JSON body.
        ctype = response.headers.get("content-type", "")
        if binary or "application/octet-stream" in ctype or not response.content:
            return response.content if binary else None
        try:
            payload = response.json()
        except Exception as exc:  # pragma: no cover - defensive
            raise SmartBillTransportError(f"Failed to decode JSON response: {exc}") from exc
        envelope = parse_envelope(payload)
        error_text, message = _extract_error(envelope)
        if error_text:
            raise SmartBillAPIError(error_text=error_text, message=message, status_code=status)
        return envelope

    # Non-2xx: try to parse an error envelope.
    error_text = ""
    message = ""
    try:
        payload = response.json()
        envelope = parse_envelope(payload)
        error_text, message = _extract_error(envelope)
    except Exception:
        error_text = response.text[:300]
    raise SmartBillAPIError(error_text=error_text, message=message, status_code=status)


class RateLimiter:
    """Simple token-bucket limiter: ``max_calls`` per ``window_seconds``.

    Optionally enabled by clients to preempt the server's 403. Thread-safe
    enough for single-threaded sync use and single-loop async use; for true
    concurrency under async, the server-side 403 is the authoritative guard.
    """

    def __init__(self, max_calls: int = 30, window_seconds: float = 10.0) -> None:
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._timestamps: list[float] = []
        self._blocked_until: float = 0.0

    def _prune(self, now: float) -> None:
        cutoff = now - self.window_seconds
        self._timestamps = [t for t in self._timestamps if t >= cutoff]

    def acquire(self) -> None:
        now = time.monotonic()
        if now < self._blocked_until:
            wait = self._blocked_until - now
            raise SmartBillRateLimitError(
                f"Client-side rate limit: would block for {wait:.1f}s."
            )
        self._prune(now)
        if len(self._timestamps) >= self.max_calls:
            self._blocked_until = self._timestamps[0] + self.window_seconds
            wait = self._blocked_until - now
            raise SmartBillRateLimitError(
                f"Client-side rate limit exceeded: would block for {wait:.1f}s."
            )
        self._timestamps.append(now)

    def notify_403(self) -> None:
        """Record a server-side 403 so the limiter backs off."""
        self._blocked_until = time.monotonic() + 600.0  # 10 minutes


__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "RateLimiter",
    "build_auth",
    "build_auth_header",
    "build_request",
    "handle_response",
    "parse_envelope",
]
