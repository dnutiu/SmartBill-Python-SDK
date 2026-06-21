"""Common shared models and enums."""

from __future__ import annotations

from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ModelConfig(BaseModel):
    """Base model with SmartBill-friendly defaults."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        use_enum_values=False,
    )


class DocumentType(str, Enum):
    """Document type for the e-mail endpoint."""

    INVOICE = "factura"
    PROFORMA = "proforma"


class PaymentType(str, Enum):
    """Possible values for ``type`` on payments / incasari."""

    CHITANTA = "Chitanta"
    BON = "Bon"
    CARD = "Card"
    CARD_ONLINE = "Card online"
    CEC = "CEC"
    BILET_ORDIN = "Bilet ordin"
    ORDIN_PLATA = "Ordin plata"
    MANDAT_POSTAL = "Mandat postal"
    EXTRAS_DE_CONT = "Extras de cont"
    RAMBURS = "Ramburs"
    ALTA_INCASARE = "Alta incasare"


class DiscountType(int, Enum):
    """Discount type: 1 = valoric, 2 = procentual."""

    VALORIC = 1
    PROCENTUAL = 2


class Client(ModelConfig):
    """Client data (``client`` / ``clientMin``)."""

    name: str = Field(..., alias="name")
    vat_code: Optional[str] = Field(None, alias="vatCode")
    code: Optional[str] = Field(None, alias="code")
    address: Optional[str] = Field(None, alias="address")
    reg_com: Optional[str] = Field(None, alias="regCom")
    is_tax_payer: Optional[bool] = Field(None, alias="isTaxPayer")
    contact: Optional[str] = Field(None, alias="contact")
    phone: Optional[str] = Field(None, alias="phone")
    city: Optional[str] = Field(None, alias="city")
    county: Optional[str] = Field(None, alias="county")
    country: Optional[str] = Field(None, alias="country")
    email: Optional[str] = Field(None, alias="email")
    bank: Optional[str] = Field(None, alias="bank")
    iban: Optional[str] = Field(None, alias="iban")
    save_to_db: Optional[bool] = Field(None, alias="saveToDb")


class Product(ModelConfig):
    """A product or discount line on an invoice / proforma / bon fiscal.

    Discount-specific fields (``number_of_items``, ``discount_type``,
    ``discount_percentage``, ``discount_value``, ``discount_tax_value``)
    are only relevant when ``is_discount`` is true.
    """

    name: str = Field(..., alias="name")
    code: Optional[str] = Field(None, alias="code")
    product_description: Optional[str] = Field(None, alias="productDescription")
    translated_name: Optional[str] = Field(None, alias="translatedName")
    translated_measuring_unit: Optional[str] = Field(None, alias="translatedMeasuringUnit")
    is_discount: Optional[bool] = Field(None, alias="isDiscount")
    number_of_items: Optional[int] = Field(None, alias="numberOfItems")
    measuring_unit_name: Optional[str] = Field(None, alias="measuringUnitName")
    currency: Optional[str] = Field(None, alias="currency")
    quantity: Optional[float] = Field(None, alias="quantity")
    price: Optional[float] = Field(None, alias="price")
    is_tax_included: Optional[bool] = Field(None, alias="isTaxIncluded")
    tax_name: Optional[str] = Field(None, alias="taxName")
    tax_percentage: Optional[float] = Field(None, alias="taxPercentage")
    exchange_rate: Optional[float] = Field(None, alias="exchangeRate")
    save_to_db: Optional[bool] = Field(None, alias="saveToDb")
    warehouse_name: Optional[str] = Field(None, alias="warehouseName")
    is_service: Optional[bool] = Field(None, alias="isService")
    # Discount fields
    discount_type: Optional[DiscountType] = Field(None, alias="discountType")
    discount_percentage: Optional[float] = Field(None, alias="discountPercentage")
    discount_value: Optional[float] = Field(None, alias="discountValue")
    discount_tax_value: Optional[float] = Field(None, alias="discountTaxValue")


class InvoiceRef(ModelConfig):
    """Reference to an existing document (series + number)."""

    series_name: str = Field(..., alias="seriesName")
    number: str = Field(..., alias="number")


class InvoicePayment(ModelConfig):
    """Payment-at-issuance block embedded in an :class:`Invoice`."""

    value: float = Field(..., alias="value")
    payment_series: Optional[str] = Field(None, alias="paymentSeries")
    type: Union[PaymentType, str] = Field(..., alias="type")
    is_cash: Optional[bool] = Field(None, alias="isCash")
