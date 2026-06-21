"""Service request builders shared by sync and async clients.

Each service builds the :class:`httpx.Request` for an endpoint and parses
the response. Sync and async clients inject the executor that actually
sends the request, so the per-endpoint logic is defined once.
"""

from __future__ import annotations

from typing import Any, Optional, Protocol, Type, TypeVar, Union

import httpx
from pydantic import BaseModel

from .._transport import build_request, handle_response
from ..models import (
    BaseResponse,
    EmailDocument,
    EmailResponse,
    Estimate,
    FiscalReceiptResponse,
    Invoice,
    InvoiceCreateResponse,
    InvoiceRef,
    Payment,
    PaymentStatusResponse,
    ProformaInvoicesResponse,
    SeriesListResponse,
    StornoRequest,
    StornoResponse,
    StocksResponse,
    TaxesResponse,
)

T = TypeVar("T", bound=BaseModel)


class _Executor(Protocol):
    """Minimal executor interface used by services."""

    base_url: str
    auth_header: str

    def execute(self, request: httpx.Request, *, binary: bool = False) -> Any: ...


def _dump(model: BaseModel, envelope_key: Optional[str]) -> Any:
    """Serialize a model, optionally wrapping it in an envelope."""
    data = model.model_dump(by_alias=True, exclude_none=True)
    if envelope_key:
        return {envelope_key: data}
    return data


def _parse(payload: Any, model: Type[T]) -> T:
    if payload is None:
        return model()
    if isinstance(payload, dict):
        return model.model_validate(payload)
    # payloads that are scalars/arrays shouldn't reach here for these models
    return model.model_validate({"message": str(payload)})


class InvoicesService:
    """``/invoice`` endpoints."""

    def __init__(self, executor: _Executor) -> None:
        self._exec = executor

    def _create_request(self, invoice: Invoice) -> httpx.Request:
        return build_request(
            method="POST",
            base_url=self._exec.base_url,
            path="invoice",
            json_body=_dump(invoice, None),
            auth_header=self._exec.auth_header,
        )

    def _delete_request(self, cif: str, series_name: str, number: str) -> httpx.Request:
        return build_request(
            method="DELETE",
            base_url=self._exec.base_url,
            path="invoice",
            params={"cif": cif, "seriesName": series_name, "number": number},
            auth_header=self._exec.auth_header,
        )

    def _reverse_request(self, storno: StornoRequest) -> httpx.Request:
        return build_request(
            method="POST",
            base_url=self._exec.base_url,
            path="invoice/reverse",
            json_body=_dump(storno, None),
            auth_header=self._exec.auth_header,
        )

    def _cancel_restore_request(self, op: str, cif: str, series_name: str, number: str) -> httpx.Request:
        return build_request(
            method="PUT",
            base_url=self._exec.base_url,
            path=f"invoice/{op}",
            params={"cif": cif, "seriesName": series_name, "number": number},
            auth_header=self._exec.auth_header,
        )

    def _payment_status_request(self, cif: str, series_name: str, number: str) -> httpx.Request:
        return build_request(
            method="GET",
            base_url=self._exec.base_url,
            path="invoice/paymentstatus",
            params={"cif": cif, "seriesName": series_name, "number": number},
            auth_header=self._exec.auth_header,
        )

    def _pdf_request(self, cif: str, series_name: str, number: str) -> httpx.Request:
        return build_request(
            method="GET",
            base_url=self._exec.base_url,
            path="invoice/pdf",
            params={"cif": cif, "seriesName": series_name, "number": number},
            accept="application/octet-stream",
            auth_header=self._exec.auth_header,
        )

    # --- sync ---
    def create(self, invoice: Invoice) -> InvoiceCreateResponse:
        r = self._exec.execute(self._create_request(invoice))
        return _parse(r, InvoiceCreateResponse)

    def delete(self, cif: str, series_name: str, number: str) -> BaseResponse:
        r = self._exec.execute(self._delete_request(cif, series_name, number))
        return _parse(r, BaseResponse)

    def reverse(self, storno: StornoRequest) -> StornoResponse:
        r = self._exec.execute(self._reverse_request(storno))
        return _parse(r, StornoResponse)

    def cancel(self, cif: str, series_name: str, number: str) -> BaseResponse:
        r = self._exec.execute(self._cancel_restore_request("cancel", cif, series_name, number))
        return _parse(r, BaseResponse)

    def restore(self, cif: str, series_name: str, number: str) -> BaseResponse:
        r = self._exec.execute(self._cancel_restore_request("restore", cif, series_name, number))
        return _parse(r, BaseResponse)

    def payment_status(self, cif: str, series_name: str, number: str) -> PaymentStatusResponse:
        r = self._exec.execute(self._payment_status_request(cif, series_name, number))
        return _parse(r, PaymentStatusResponse)

    def pdf(self, cif: str, series_name: str, number: str) -> bytes:
        return self._exec.execute(self._pdf_request(cif, series_name, number), binary=True)

    # --- async ---
    async def acreate(self, invoice: Invoice) -> InvoiceCreateResponse:
        r = await self._exec.aexecute(self._create_request(invoice))
        return _parse(r, InvoiceCreateResponse)

    async def adelete(self, cif: str, series_name: str, number: str) -> BaseResponse:
        r = await self._exec.aexecute(self._delete_request(cif, series_name, number))
        return _parse(r, BaseResponse)

    async def areverse(self, storno: StornoRequest) -> StornoResponse:
        r = await self._exec.aexecute(self._reverse_request(storno))
        return _parse(r, StornoResponse)

    async def acancel(self, cif: str, series_name: str, number: str) -> BaseResponse:
        r = await self._exec.aexecute(self._cancel_restore_request("cancel", cif, series_name, number))
        return _parse(r, BaseResponse)

    async def arestore(self, cif: str, series_name: str, number: str) -> BaseResponse:
        r = await self._exec.aexecute(self._cancel_restore_request("restore", cif, series_name, number))
        return _parse(r, BaseResponse)

    async def apayment_status(self, cif: str, series_name: str, number: str) -> PaymentStatusResponse:
        r = await self._exec.aexecute(self._payment_status_request(cif, series_name, number))
        return _parse(r, PaymentStatusResponse)

    async def apdf(self, cif: str, series_name: str, number: str) -> bytes:
        return await self._exec.aexecute(self._pdf_request(cif, series_name, number), binary=True)


class EstimatesService:
    """``/estimate`` endpoints."""

    def __init__(self, executor: _Executor) -> None:
        self._exec = executor

    def _create_request(self, estimate: Estimate) -> httpx.Request:
        return build_request(
            method="POST", base_url=self._exec.base_url, path="estimate",
            json_body=_dump(estimate, None), auth_header=self._exec.auth_header,
        )

    def _delete_request(self, cif: str, series_name: str, number: str) -> httpx.Request:
        return build_request(
            method="DELETE", base_url=self._exec.base_url, path="estimate",
            params={"cif": cif, "seriesName": series_name, "number": number},
            auth_header=self._exec.auth_header,
        )

    def _cancel_restore_request(self, op: str, cif: str, series_name: str, number: str) -> httpx.Request:
        return build_request(
            method="PUT", base_url=self._exec.base_url, path=f"estimate/{op}",
            params={"cif": cif, "seriesName": series_name, "number": number},
            auth_header=self._exec.auth_header,
        )

    def _pdf_request(self, cif: str, series_name: str, number: str) -> httpx.Request:
        return build_request(
            method="GET", base_url=self._exec.base_url, path="estimate/pdf",
            params={"cif": cif, "seriesName": series_name, "number": number},
            accept="application/octet-stream", auth_header=self._exec.auth_header,
        )

    def _invoices_request(self, cif: str, series_name: str, number: str) -> httpx.Request:
        return build_request(
            method="GET", base_url=self._exec.base_url, path="estimate/invoices",
            params={"cif": cif, "seriesName": series_name, "number": number},
            auth_header=self._exec.auth_header,
        )

    def create(self, estimate: Estimate) -> InvoiceCreateResponse:
        return _parse(self._exec.execute(self._create_request(estimate)), InvoiceCreateResponse)

    def delete(self, cif: str, series_name: str, number: str) -> BaseResponse:
        return _parse(self._exec.execute(self._delete_request(cif, series_name, number)), BaseResponse)

    def cancel(self, cif: str, series_name: str, number: str) -> BaseResponse:
        return _parse(self._exec.execute(self._cancel_restore_request("cancel", cif, series_name, number)), BaseResponse)

    def restore(self, cif: str, series_name: str, number: str) -> BaseResponse:
        return _parse(self._exec.execute(self._cancel_restore_request("restore", cif, series_name, number)), BaseResponse)

    def pdf(self, cif: str, series_name: str, number: str) -> bytes:
        return self._exec.execute(self._pdf_request(cif, series_name, number), binary=True)

    def invoices_status(self, cif: str, series_name: str, number: str) -> ProformaInvoicesResponse:
        return _parse(self._exec.execute(self._invoices_request(cif, series_name, number)), ProformaInvoicesResponse)

    async def acreate(self, estimate: Estimate) -> InvoiceCreateResponse:
        return _parse(await self._exec.aexecute(self._create_request(estimate)), InvoiceCreateResponse)

    async def adelete(self, cif: str, series_name: str, number: str) -> BaseResponse:
        return _parse(await self._exec.aexecute(self._delete_request(cif, series_name, number)), BaseResponse)

    async def acancel(self, cif: str, series_name: str, number: str) -> BaseResponse:
        return _parse(await self._exec.aexecute(self._cancel_restore_request("cancel", cif, series_name, number)), BaseResponse)

    async def arestore(self, cif: str, series_name: str, number: str) -> BaseResponse:
        return _parse(await self._exec.aexecute(self._cancel_restore_request("restore", cif, series_name, number)), BaseResponse)

    async def apdf(self, cif: str, series_name: str, number: str) -> bytes:
        return await self._exec.aexecute(self._pdf_request(cif, series_name, number), binary=True)

    async def ainvoices_status(self, cif: str, series_name: str, number: str) -> ProformaInvoicesResponse:
        return _parse(await self._exec.aexecute(self._invoices_request(cif, series_name, number)), ProformaInvoicesResponse)


class PaymentsService:
    """``/payment`` endpoints."""

    def __init__(self, executor: _Executor) -> None:
        self._exec = executor

    def _create_request(self, payment: Payment) -> httpx.Request:
        return build_request(
            method="POST", base_url=self._exec.base_url, path="payment",
            json_body=_dump(payment, None), auth_header=self._exec.auth_header,
        )

    def _delete_other_request(self, cif: str, **opts: Any) -> httpx.Request:
        params: dict[str, Any] = {"cif": cif}
        for key in ("paymentType", "paymentDate", "paymentValue",
                    "clientName", "clientCif", "invoiceSeries", "invoiceNumber"):
            snake = {
                "paymentType": "payment_type", "paymentDate": "payment_date",
                "paymentValue": "payment_value", "clientName": "client_name",
                "clientCif": "client_cif", "invoiceSeries": "invoice_series",
                "invoiceNumber": "invoice_number",
            }[key]
            if opts.get(snake) is not None:
                params[key] = opts[snake]
        return build_request(
            method="DELETE", base_url=self._exec.base_url, path="payment/v2",
            params=params, auth_header=self._exec.auth_header,
        )

    def _delete_chitanta_request(self, cif: str, series_name: str, number: str) -> httpx.Request:
        return build_request(
            method="DELETE", base_url=self._exec.base_url, path="payment/chitanta",
            params={"cif": cif, "seriesName": series_name, "number": number},
            auth_header=self._exec.auth_header,
        )

    def _receipt_text_request(self, cif: str, id: str) -> httpx.Request:
        return build_request(
            method="GET", base_url=self._exec.base_url, path="payment/text",
            params={"cif": cif, "id": id}, auth_header=self._exec.auth_header,
        )

    def create(self, payment: Payment) -> FiscalReceiptResponse:
        return _parse(self._exec.execute(self._create_request(payment)), FiscalReceiptResponse)

    def delete_other(self, cif: str, *, payment_type: str,
                     payment_date: Optional[str] = None,
                     payment_value: Optional[float] = None,
                     client_name: Optional[str] = None,
                     client_cif: Optional[str] = None,
                     invoice_series: Optional[str] = None,
                     invoice_number: Optional[str] = None) -> BaseResponse:
        r = self._exec.execute(self._delete_other_request(
            cif, payment_type=payment_type, payment_date=payment_date,
            payment_value=payment_value, client_name=client_name,
            client_cif=client_cif, invoice_series=invoice_series,
            invoice_number=invoice_number))
        return _parse(r, BaseResponse)

    def delete_chitanta(self, cif: str, series_name: str, number: str) -> BaseResponse:
        return _parse(self._exec.execute(self._delete_chitanta_request(cif, series_name, number)), BaseResponse)

    def fiscal_receipt_text(self, cif: str, id: str) -> FiscalReceiptResponse:
        return _parse(self._exec.execute(self._receipt_text_request(cif, id)), FiscalReceiptResponse)

    async def acreate(self, payment: Payment) -> FiscalReceiptResponse:
        return _parse(await self._exec.aexecute(self._create_request(payment)), FiscalReceiptResponse)

    async def adelete_other(self, cif: str, *, payment_type: str,
                            payment_date: Optional[str] = None,
                            payment_value: Optional[float] = None,
                            client_name: Optional[str] = None,
                            client_cif: Optional[str] = None,
                            invoice_series: Optional[str] = None,
                            invoice_number: Optional[str] = None) -> BaseResponse:
        r = await self._exec.aexecute(self._delete_other_request(
            cif, payment_type=payment_type, payment_date=payment_date,
            payment_value=payment_value, client_name=client_name,
            client_cif=client_cif, invoice_series=invoice_series,
            invoice_number=invoice_number))
        return _parse(r, BaseResponse)

    async def adelete_chitanta(self, cif: str, series_name: str, number: str) -> BaseResponse:
        return _parse(await self._exec.aexecute(self._delete_chitanta_request(cif, series_name, number)), BaseResponse)

    async def afiscal_receipt_text(self, cif: str, id: str) -> FiscalReceiptResponse:
        return _parse(await self._exec.aexecute(self._receipt_text_request(cif, id)), FiscalReceiptResponse)


class EmailService:
    """``/document/send`` endpoint."""

    def __init__(self, executor: _Executor) -> None:
        self._exec = executor

    def _request(self, email: EmailDocument) -> httpx.Request:
        return build_request(
            method="POST", base_url=self._exec.base_url, path="document/send",
            json_body=_dump(email, None), auth_header=self._exec.auth_header,
        )

    def send(self, email: EmailDocument) -> EmailResponse:
        return _parse(self._exec.execute(self._request(email)), EmailResponse)

    async def asend(self, email: EmailDocument) -> EmailResponse:
        return _parse(await self._exec.aexecute(self._request(email)), EmailResponse)


class ConfigurationService:
    """``/tax`` and ``/series`` endpoints."""

    def __init__(self, executor: _Executor) -> None:
        self._exec = executor

    def _taxes_request(self, cif: str) -> httpx.Request:
        return build_request(
            method="GET", base_url=self._exec.base_url, path="tax",
            params={"cif": cif}, auth_header=self._exec.auth_header,
        )

    def _series_request(self, cif: str, type: Optional[str] = None) -> httpx.Request:
        params: dict[str, Any] = {"cif": cif}
        if type is not None:
            params["type"] = type
        return build_request(
            method="GET", base_url=self._exec.base_url, path="series",
            params=params, auth_header=self._exec.auth_header,
        )

    def taxes(self, cif: str) -> TaxesResponse:
        return _parse(self._exec.execute(self._taxes_request(cif)), TaxesResponse)

    def series(self, cif: str, type: Optional[str] = None) -> SeriesListResponse:
        return _parse(self._exec.execute(self._series_request(cif, type)), SeriesListResponse)

    async def ataxes(self, cif: str) -> TaxesResponse:
        return _parse(await self._exec.aexecute(self._taxes_request(cif)), TaxesResponse)

    async def aseries(self, cif: str, type: Optional[str] = None) -> SeriesListResponse:
        return _parse(await self._exec.aexecute(self._series_request(cif, type)), SeriesListResponse)


class StocksService:
    """``/stocks`` endpoint."""

    def __init__(self, executor: _Executor) -> None:
        self._exec = executor

    def _request(self, cif: str, date: str,
                 warehouse_name: Optional[str] = None,
                 product_name: Optional[str] = None,
                 product_code: Optional[str] = None) -> httpx.Request:
        params: dict[str, Any] = {"cif": cif, "date": date}
        if warehouse_name is not None:
            params["warehouseName"] = warehouse_name
        if product_name is not None:
            params["productName"] = product_name
        if product_code is not None:
            params["productCode"] = product_code
        return build_request(
            method="GET", base_url=self._exec.base_url, path="stocks",
            params=params, auth_header=self._exec.auth_header,
        )

    def get(self, cif: str, date: str, *,
            warehouse_name: Optional[str] = None,
            product_name: Optional[str] = None,
            product_code: Optional[str] = None) -> StocksResponse:
        r = self._exec.execute(self._request(cif, date, warehouse_name, product_name, product_code))
        return _parse(r, StocksResponse)

    async def aget(self, cif: str, date: str, *,
                   warehouse_name: Optional[str] = None,
                   product_name: Optional[str] = None,
                   product_code: Optional[str] = None) -> StocksResponse:
        r = await self._exec.aexecute(self._request(cif, date, warehouse_name, product_name, product_code))
        return _parse(r, StocksResponse)


__all__ = [
    "ConfigurationService",
    "EmailService",
    "EstimatesService",
    "InvoicesService",
    "PaymentsService",
    "StocksService",
]
