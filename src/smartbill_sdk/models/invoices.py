"""Invoice models."""

from __future__ import annotations

from typing import List, Optional, Union

from pydantic import Field

from .common import Client, InvoicePayment, InvoiceRef, ModelConfig, PaymentType, Product


class Invoice(ModelConfig):
    """Request body for ``POST /invoice`` (emitere factura).

    The JSON is wrapped in an ``{"invoice": {...}}`` envelope when sent.
    """

    company_vat_code: str = Field(..., alias="companyVatCode")
    client: Optional[Client] = Field(None, alias="client")
    is_draft: Optional[bool] = Field(None, alias="isDraft")
    issue_date: Optional[str] = Field(None, alias="issueDate")
    series_name: Optional[str] = Field(None, alias="seriesName")
    currency: Optional[str] = Field(None, alias="currency")
    exchange_rate: Optional[float] = Field(None, alias="exchangeRate")
    language: Optional[str] = Field(None, alias="language")
    precision: Optional[int] = Field(None, alias="precision")
    issuer_cnp: Optional[str] = Field(None, alias="issuerCnp")
    issuer_name: Optional[str] = Field(None, alias="issuerName")
    aviz: Optional[str] = Field(None, alias="aviz")
    due_date: Optional[str] = Field(None, alias="dueDate")
    mentions: Optional[str] = Field(None, alias="mentions")
    observations: Optional[str] = Field(None, alias="observations")
    delegate_auto: Optional[str] = Field(None, alias="delegateAuto")
    delegate_identity_card: Optional[str] = Field(None, alias="delegateIdentityCard")
    delegate_name: Optional[str] = Field(None, alias="delegateName")
    delivery_date: Optional[str] = Field(None, alias="deliveryDate")
    payment_date: Optional[str] = Field(None, alias="paymentDate")
    use_stock: Optional[bool] = Field(None, alias="useStock")
    use_estimate_details: Optional[bool] = Field(None, alias="useEstimateDetails")
    use_payment_tax: Optional[bool] = Field(None, alias="usePaymentTax")
    payment_base: Optional[float] = Field(None, alias="paymentBase")
    colected_tax: Optional[float] = Field(None, alias="colectedTax")
    payment_total: Optional[float] = Field(None, alias="paymentTotal")
    payment_url: Optional[str] = Field(None, alias="paymentUrl")
    estimate: Optional[InvoiceRef] = Field(None, alias="estimate")
    products: List[Product] = Field(default_factory=list, alias="products")
    payment: Optional[InvoicePayment] = Field(None, alias="payment")


class StornoRequest(ModelConfig):
    """Request body for ``POST /invoice/reverse`` (stornare factura).

    Sent as a bare object (no envelope).
    """

    company_vat_code: str = Field(..., alias="companyVatCode")
    series_name: str = Field(..., alias="seriesName")
    number: str = Field(..., alias="number")
    issue_date: Optional[str] = Field(None, alias="issueDate")
