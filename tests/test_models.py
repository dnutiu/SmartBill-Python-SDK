"""Tests for pydantic models: aliasing, enums, envelopes."""

import json

import pytest
from pydantic import ValidationError

from smartbill_sdk.models import (
    Client,
    DiscountType,
    DocumentType,
    EmailDocument,
    Estimate,
    Invoice,
    InvoicePayment,
    InvoiceRef,
    Payment,
    PaymentType,
    Product,
    StornoRequest,
)


def test_invoice_aliasing_round_trip():
    inv = Invoice(
        company_vat_code="RO12345678",
        client=Client(name="Intelligent IT", vat_code="RO123", save_to_db=False),
        is_draft=False,
        series_name="FCT",
        precision=2,
        products=[
            Product(name="P1", measuring_unit_name="buc", currency="RON",
                    quantity=2, price=10, is_tax_included=True,
                    tax_name="Redusa", tax_percentage=9),
        ],
    )
    dumped = inv.model_dump(by_alias=True, exclude_none=True)
    assert dumped["companyVatCode"] == "RO12345678"
    assert dumped["client"]["vatCode"] == "RO123"
    assert dumped["products"][0]["measuringUnitName"] == "buc"
    assert dumped["products"][0]["isTaxIncluded"] is True

    # Round-trip back.
    again = Invoice.model_validate(dumped)
    assert again.company_vat_code == "RO12345678"
    assert again.client.vat_code == "RO123"
    assert again.products[0].measuring_unit_name == "buc"


def test_product_discount_fields_optional():
    p = Product(name="Discount", is_discount=True, number_of_items=2,
                measuring_unit_name="buc", currency="RON",
                discount_type=DiscountType.PROCENTUAL, discount_percentage=10)
    dumped = p.model_dump(by_alias=True, exclude_none=True)
    assert dumped["isDiscount"] is True
    assert dumped["discountType"] == 2
    assert dumped["discountPercentage"] == 10


def test_payment_enum_serializes_to_value():
    pay = Payment(company_vat_code="RO1", value=100, type=PaymentType.ORDIN_PLATA)
    dumped = pay.model_dump(by_alias=True, exclude_none=True)
    assert dumped["type"] == "Ordin plata"


def test_payment_accepts_plain_string_type():
    pay = Payment(company_vat_code="RO1", value=100, type="Chitanta")
    assert pay.type == "Chitanta"


def test_invoice_payment_required_fields():
    ip = InvoicePayment(value=50, type="Card")
    dumped = ip.model_dump(by_alias=True, exclude_none=True)
    assert dumped == {"value": 50.0, "type": "Card"}


def test_invoice_ref_aliasing():
    ref = InvoiceRef(series_name="FCT", number="14")
    assert ref.model_dump(by_alias=True) == {"seriesName": "FCT", "number": "14"}


def test_estimate_basic():
    est = Estimate(company_vat_code="RO1", client=Client(name="C"),
                   series_name="PFC", products=[])
    dumped = est.model_dump(by_alias=True, exclude_none=True)
    assert dumped["companyVatCode"] == "RO1"
    assert dumped["client"]["name"] == "C"


def test_email_document_aliasing():
    e = EmailDocument(company_vat_code="RO1", series_name="FCT", number="0040",
                      type=DocumentType.INVOICE, to="a@b.ro")
    dumped = e.model_dump(by_alias=True, exclude_none=True)
    assert dumped["type"] == "factura"
    assert dumped["to"] == "a@b.ro"


def test_storno_request():
    s = StornoRequest(company_vat_code="RO1", series_name="FFF", number="0985")
    dumped = s.model_dump(by_alias=True, exclude_none=True)
    assert dumped == {"companyVatCode": "RO1", "seriesName": "FFF", "number": "0985"}


def test_invoice_requires_company_vat_code():
    with pytest.raises(ValidationError):
        Invoice(client=Client(name="x"))


def test_client_requires_name():
    with pytest.raises(ValidationError):
        Client(vat_code="RO1")
