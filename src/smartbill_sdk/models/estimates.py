"""Proforma (estimate) models."""

from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from .common import Client, ModelConfig, Product


class Estimate(ModelConfig):
    """Request body for ``POST /estimate`` (emitere proforma).

    Wrapped in an ``{"estimate": {...}}`` envelope when sent.
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
    delegate_name: Optional[str] = Field(None, alias="delegateName")
    delegate_identity_card: Optional[str] = Field(None, alias="delegateIdentityCard")
    delegate_auto: Optional[str] = Field(None, alias="delegateAuto")
    payment_url: Optional[str] = Field(None, alias="paymentUrl")
    use_stock: Optional[bool] = Field(None, alias="useStock")
    products: List[Product] = Field(default_factory=list, alias="products")
