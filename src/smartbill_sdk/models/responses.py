"""Response models for SmartBill endpoints."""

from __future__ import annotations

from typing import List, Optional, Union

from pydantic import Field

from .common import InvoiceRef, ModelConfig


class BaseResponse(ModelConfig):
    """Common envelope: ``errorText``/``message``/``number``/``series``/``url``."""

    error_text: Optional[str] = Field(None, alias="errorText")
    message: Optional[str] = Field(None, alias="message")
    number: Optional[str] = Field(None, alias="number")
    series: Optional[str] = Field(None, alias="series")
    url: Optional[str] = Field(None, alias="url")


class InvoiceCreateResponse(BaseResponse):
    """Response for invoice / proforma creation."""


class StornoResponse(BaseResponse):
    """Response for ``POST /invoice/reverse``."""

    document_url: Optional[str] = Field(None, alias="documentUrl")
    document_id: Optional[Union[str, int]] = Field(None, alias="documentId")
    document_view_url: Optional[str] = Field(None, alias="documentViewUrl")


class PaymentStatusResponse(ModelConfig):
    """Response for ``GET /invoice/paymentstatus``."""

    error_text: Optional[str] = Field(None, alias="errorText")
    message: Optional[str] = Field(None, alias="message")
    number: Optional[str] = Field(None, alias="number")
    series: Optional[str] = Field(None, alias="series")
    invoice_total_amount: Optional[float] = Field(None, alias="invoiceTotalAmount")
    paid_amount: Optional[float] = Field(None, alias="paidAmount")
    unpaid_amount: Optional[float] = Field(None, alias="unpaidAmount")
    paid: Optional[bool] = Field(None, alias="paid")


class ProformaInvoicesResponse(BaseResponse):
    """Response for ``GET /estimate/invoices``."""

    are_invoices_created: Optional[bool] = Field(None, alias="areInvoicesCreated")
    invoices: List[InvoiceRef] = Field(default_factory=list, alias="invoices")


class EmailStatus(ModelConfig):
    code: Optional[Union[str, int]] = Field(None, alias="code")
    message: Optional[str] = Field(None, alias="message")


class EmailResponse(ModelConfig):
    """Response for ``POST /document/send`` (``Response.status``)."""

    status: Optional[EmailStatus] = Field(None, alias="status")


class FiscalReceiptResponse(BaseResponse):
    """Response for ``GET /payment/text`` (bon fiscal content, base64)."""

    id: Optional[Union[str, int]] = Field(None, alias="id")
