"""Exception hierarchy for the SmartBill SDK."""

from __future__ import annotations

from typing import Optional


class SmartBillError(Exception):
    """Base class for all SDK errors."""


class SmartBillAuthError(SmartBillError):
    """Raised on HTTP 401 (bad credentials / company)."""


class SmartBillRateLimitError(SmartBillError):
    """Raised on HTTP 403 (rate limit exceeded — access blocked 10 min)."""


class SmartBillAPIError(SmartBillError):
    """Raised when the SmartBill API returns an error envelope.

    Attributes:
        error_text: The ``errorText`` field from the API response.
        message:    The optional ``message`` field from the API response.
        status_code: HTTP status code of the response, if available.
    """

    def __init__(
        self,
        error_text: str = "",
        message: str = "",
        status_code: Optional[int] = None,
    ) -> None:
        self.error_text = error_text
        self.message = message
        self.status_code = status_code
        detail = error_text or message or "SmartBill API error"
        if status_code is not None:
            detail = f"[{status_code}] {detail}"
        super().__init__(detail)


class SmartBillTransportError(SmartBillError):
    """Raised when a network/transport-level failure occurs."""
