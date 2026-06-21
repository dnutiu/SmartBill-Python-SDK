"""Payment (incasare) models."""

from __future__ import annotations

from typing import List, Optional, Union

from pydantic import Field

from .common import Client, InvoiceRef, ModelConfig, PaymentType, Product


class Payment(ModelConfig):
    """Request body for ``POST /payment``.

    Covers general incasari, chitanta, and bon fiscal. Fields unused for a
    given ``type`` are simply left as ``None``. Wrapped in a
    ``{"payment": {...}}`` envelope when sent.

    Bon-fiscal payment-method fields (``received_*``) are all optional and
    default to 0 on the server side.
    """

    company_vat_code: str = Field(..., alias="companyVatCode")
    client: Optional[Client] = Field(None, alias="client")
    issue_date: Optional[str] = Field(None, alias="issueDate")
    currency: Optional[str] = Field(None, alias="currency")
    language: Optional[str] = Field(None, alias="language")
    exchange_rate: Optional[float] = Field(None, alias="exchangeRate")
    precision: Optional[int] = Field(None, alias="precision")
    issuer_cnp: Optional[str] = Field(None, alias="issuerCnp")
    series_name: Optional[str] = Field(None, alias="seriesName")
    number: Optional[str] = Field(None, alias="number")
    value: Optional[float] = Field(None, alias="value")
    text: Optional[str] = Field(None, alias="text")
    translated_text: Optional[str] = Field(None, alias="translatedText")
    is_draft: Optional[bool] = Field(None, alias="isDraft")
    type: Union[PaymentType, str] = Field(None, alias="type")
    is_cash: Optional[bool] = Field(None, alias="isCash")
    observation: Optional[str] = Field(None, alias="observation")
    use_invoice_details: Optional[bool] = Field(None, alias="useInvoiceDetails")
    invoices_list: Optional[List[InvoiceRef]] = Field(None, alias="invoicesList")
    # Bon fiscal
    return_fiscal_printer_text: Optional[bool] = Field(None, alias="returnFiscalPrinterText")
    use_stock: Optional[bool] = Field(None, alias="useStock")
    products: Optional[List[Product]] = Field(None, alias="products")
    received_cash: Optional[float] = Field(None, alias="receivedCash")
    received_card: Optional[float] = Field(None, alias="receivedCard")
    received_tichete_masa: Optional[float] = Field(None, alias="receivedTicheteMasa")
    received_tichete_cadou: Optional[float] = Field(None, alias="receivedTicheteCadou")
    received_ordin_de_plata: Optional[float] = Field(None, alias="receivedOrdinDePlata")
    received_cec: Optional[float] = Field(None, alias="receivedCec")
    received_credit: Optional[float] = Field(None, alias="receivedCredit")
    received_cupon: Optional[float] = Field(None, alias="receivedCupon")
    received_puncte_de_fidelitate: Optional[float] = Field(None, alias="receivedPuncteDeFidelitate")
    received_bonuri_valoare_fixa: Optional[float] = Field(None, alias="receivedBonuriValoareFixa")
    received_moneda_alternativa: Optional[float] = Field(None, alias="receivedMonedaAlternativa")
