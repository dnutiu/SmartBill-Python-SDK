"""Endpoint tests for PaymentsService via respx."""

import json

import httpx
import respx

from smartbill_sdk.models import Client, InvoiceRef, Payment, PaymentType

from conftest import BASE, envelope, make_sync_client, make_async_client


@respx.mock
def test_payment_create_general_sync():
    route = respx.post(f"{BASE}payment").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", number="0030", series="CHT")))
    c = make_sync_client()
    pay = Payment(company_vat_code="RO1", client=Client(name="X"), value=14,
                  type=PaymentType.ORDIN_PLATA, is_cash=False,
                  invoices_list=[InvoiceRef(series_name="FCT", number="14")])
    r = c.payments.create(pay)
    assert r.series == "CHT"
    payload = json.loads(route.calls[0].request.read())
    assert payload["companyVatCode"] == "RO1"
    assert payload["type"] == "Ordin plata"
    assert payload["invoicesList"][0]["seriesName"] == "FCT"
    c.close()


@respx.mock
async def test_payment_create_chitanta_async():
    respx.post(f"{BASE}payment").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", number="1", series="CHT")))
    ac = make_async_client()
    pay = Payment(company_vat_code="RO1", client=Client(name="X"),
                  value=14, type=PaymentType.CHITANTA, series_name="CHT")
    r = await ac.payments.acreate(pay)
    assert r.number == "1"
    await ac.aclose()


@respx.mock
def test_payment_delete_other_by_invoice_sync():
    route = respx.delete(f"{BASE}payment/v2").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", message="ok")))
    c = make_sync_client()
    c.payments.delete_other("RO1", payment_type="Ordin plata",
                            invoice_series="FCT", invoice_number="0024")
    p = route.calls[0].request.url.params
    assert p["cif"] == "RO1"
    assert p["paymentType"] == "Ordin plata"
    assert p["invoiceSeries"] == "FCT"
    assert p["invoiceNumber"] == "0024"
    # unused optional params should not be present
    assert "paymentDate" not in p
    c.close()


@respx.mock
def test_payment_delete_other_by_params_sync():
    route = respx.delete(f"{BASE}payment/v2").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", message="ok")))
    c = make_sync_client()
    c.payments.delete_other("RO1", payment_type="Card",
                            payment_date="2021-02-15", payment_value=20,
                            client_name="Intelligent IT", client_cif="RO12345678")
    p = route.calls[0].request.url.params
    assert p["paymentDate"] == "2021-02-15"
    assert p["paymentValue"] == "20"
    assert p["clientName"] == "Intelligent IT"
    assert p["clientCif"] == "RO12345678"
    assert "invoiceSeries" not in p
    c.close()


@respx.mock
async def test_payment_delete_other_async():
    respx.delete(f"{BASE}payment/v2").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", message="ok")))
    ac = make_async_client()
    await ac.payments.adelete_other("RO1", payment_type="CEC", invoice_series="FCT",
                                    invoice_number="1")
    await ac.aclose()


@respx.mock
def test_payment_delete_chitanta_sync():
    route = respx.delete(f"{BASE}payment/chitanta").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", message="ok")))
    c = make_sync_client()
    c.payments.delete_chitanta("RO1", "CHT", "0115")
    p = route.calls[0].request.url.params
    assert p["seriesName"] == "CHT"
    assert p["number"] == "0115"
    c.close()


@respx.mock
def test_payment_fiscal_receipt_text_sync():
    respx.get(f"{BASE}payment/text").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcResponse", message="UCwxLF9f", number="", series="")))
    c = make_sync_client()
    r = c.payments.fiscal_receipt_text("RO1", "12345")
    assert r.message == "UCwxLF9f"
    c.close()


@respx.mock
async def test_payment_fiscal_receipt_text_async():
    respx.get(f"{BASE}payment/text").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", message="UCwxLF9f")))
    ac = make_async_client()
    r = await ac.payments.afiscal_receipt_text("RO1", "12345")
    assert r.message == "UCwxLF9f"
    await ac.aclose()


@respx.mock
def test_payment_bon_fiscal_received_fields_serialized():
    route = respx.post(f"{BASE}payment").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", id="12345", number="12")))
    c = make_sync_client()
    pay = Payment(company_vat_code="RO1", value=260, type="Bon", number="",
                  return_fiscal_printer_text=True, use_stock=False,
                  received_cash=200, received_card=60)
    resp = c.payments.create(pay)
    assert resp.id == "12345"
    assert resp.number == "12"
    payload = json.loads(route.calls[0].request.read())
    assert payload["receivedCash"] == 200
    assert payload["receivedCard"] == 60
    assert payload["returnFiscalPrinterText"] is True
    c.close()
