"""Synchronous SmartBill client."""

from __future__ import annotations

from typing import Any, Optional

import httpx

from ._transport import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    RateLimiter,
    build_auth,
    handle_response,
)
from .exceptions import SmartBillError, SmartBillRateLimitError
from .services import (
    ConfigurationService,
    EmailService,
    EstimatesService,
    InvoicesService,
    PaymentsService,
    StocksService,
)


class SmartBillClient:
    """Synchronous client for the SmartBill Cloud REST API.

    Usage::

        client = SmartBillClient(username="you@example.com", token="...")
        resp = client.invoices.create(invoice)
        client.close()

    Or as a context manager::

        with SmartBillClient(...) as client:
            ...
    """

    def __init__(
        self,
        username: str,
        token: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        enforce_rate_limit: bool = False,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self.username = username
        self.token = token
        self.base_url = base_url
        self.auth_header = build_auth(username, token)
        self._rate_limiter = RateLimiter() if enforce_rate_limit else None
        self._owns_client = client is None
        self._http = client or httpx.Client(timeout=timeout)
        # Services (lazily nothing — they're cheap).
        self.invoices = InvoicesService(self)
        self.estimates = EstimatesService(self)
        self.payments = PaymentsService(self)
        self.email = EmailService(self)
        self.taxes = ConfigurationService(self)  # convenience alias below
        self.series = self.taxes
        self.stocks = StocksService(self)

    # --- executor interface used by services ---
    def execute(self, request: httpx.Request, *, binary: bool = False) -> Any:
        if self._rate_limiter is not None:
            try:
                self._rate_limiter.acquire()
            except SmartBillRateLimitError:
                raise
        try:
            response = self._http.send(request)
        except httpx.HTTPError as exc:
            raise SmartBillError(f"Transport error: {exc}") from exc
        if response.status_code == 403 and self._rate_limiter is not None:
            self._rate_limiter.notify_403()
        return handle_response(response, binary=binary)

    # async services call this; raise a clear error if used wrongly.
    async def aexecute(self, request: httpx.Request, *, binary: bool = False) -> Any:  # pragma: no cover
        raise SmartBillError(
            "aexecute() called on a sync SmartBillClient. "
            "Use AsyncSmartBillClient for async access."
        )

    # --- lifecycle ---
    def close(self) -> None:
        if self._owns_client:
            self._http.close()

    def __enter__(self) -> "SmartBillClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


__all__ = ["SmartBillClient"]
