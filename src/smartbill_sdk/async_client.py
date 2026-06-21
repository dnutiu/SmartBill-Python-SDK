"""Asynchronous SmartBill client."""

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


class AsyncSmartBillClient:
    """Asynchronous client for the SmartBill Cloud REST API.

    Usage::

        client = AsyncSmartBillClient(username="...", token="...")
        resp = await client.invoices.acreate(invoice)
        await client.aclose()

    Or as an async context manager::

        async with AsyncSmartBillClient(...) as client:
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
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.username = username
        self.token = token
        self.base_url = base_url
        self.auth_header = build_auth(username, token)
        self._rate_limiter = RateLimiter() if enforce_rate_limit else None
        self._owns_client = client is None
        self._http = client or httpx.AsyncClient(timeout=timeout)
        self.invoices = InvoicesService(self)
        self.estimates = EstimatesService(self)
        self.payments = PaymentsService(self)
        self.email = EmailService(self)
        self.taxes = ConfigurationService(self)
        self.series = self.taxes
        self.stocks = StocksService(self)

    async def aexecute(self, request: httpx.Request, *, binary: bool = False) -> Any:
        if self._rate_limiter is not None:
            self._rate_limiter.acquire()
        try:
            response = await self._http.send(request)
        except httpx.HTTPError as exc:
            raise SmartBillError(f"Transport error: {exc}") from exc
        if response.status_code == 403 and self._rate_limiter is not None:
            self._rate_limiter.notify_403()
        return handle_response(response, binary=binary)

    def execute(self, request: httpx.Request, *, binary: bool = False) -> Any:  # pragma: no cover
        raise SmartBillError(
            "execute() called on an async AsyncSmartBillClient. "
            "Use SmartBillClient for sync access."
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    async def __aenter__(self) -> "AsyncSmartBillClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()


__all__ = ["AsyncSmartBillClient"]
