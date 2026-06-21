"""E-mail (document send) models."""

from __future__ import annotations

from typing import Optional, Union

from pydantic import Field

from .common import DocumentType, ModelConfig


class EmailDocument(ModelConfig):
    """Request body for ``POST /document/send``.

    Wrapped in a ``{"sendDocumentRequest": {...}}`` envelope when sent.
    ``subject`` and ``body_text`` should be Base64-encoded by the caller
    (as required by the SmartBill API).
    """

    company_vat_code: str = Field(..., alias="companyVatCode")
    series_name: str = Field(..., alias="seriesName")
    number: str = Field(..., alias="number")
    type: Union[DocumentType, str] = Field(None, alias="type")
    subject: Optional[str] = Field(None, alias="subject")
    to: Optional[str] = Field(None, alias="to")
    cc: Optional[str] = Field(None, alias="cc")
    bcc: Optional[str] = Field(None, alias="bcc")
    body_text: Optional[str] = Field(None, alias="bodyText")
