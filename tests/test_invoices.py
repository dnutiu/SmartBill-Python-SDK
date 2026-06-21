"""Endpoint tests for InvoicesService (sync + async) via respx."""

import httpx
import pytest
import respx

from smartbill_sdk import SmartBillAPIError
from smartbill_sdk.models import Client, Invoice, Product, StornoRequest

from conftest import (
    BASE,
    assert_auth,
    assert_json_headers,
    envelope,
    make_async_client,
    make_sync_client,
)


# --- create ---
@respx.mock
def test_invoice_create_sync():
    route = respx.post(f"{BASE}invoice").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcResponse", errorText="", message="", number="0040", series="FCT")))
    c = make_sync_client()
    inv = Invoice(company_vat_code="RO1", client=Client(name="X"),
                  series_name="FCT", products=[Product(name="p", measuring_unit_name="buc",
                                                       currency="RON", quantity=1, price=10)])
    resp = c.invoices.create(inv)
    assert resp.number == "0040"
    assert resp.series == "FCT"
    req = route.calls[0].request
    assert_auth(req)
    assert_json_headers(req)
    body = req.read()
    import json
    payload = json.loads(body)
    assert payload["companyVatCode"] == "RO1"
    assert payload["client"]["name"] == "X"
    c.close()


@respx.mock
async def test_invoice_create_async():
    respx.post(f"{BASE}invoice").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcResponse", number="0001", series="FCT")))
    ac = make_async_client()
    inv = Invoice(company_vat_code="RO1", client=Client(name="X"), products=[])
    resp = await ac.invoices.acreate(inv)
    assert resp.number == "0001"
    await ac.aclose()


# --- delete ---
@respx.mock
def test_invoice_delete_sync():
    route = respx.delete(url__regex=rf"{BASE}invoice\?.*").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcResponse", message="Factura cu seria si numarul FCT0040 a fost stearsa cu succes.")))
    c = make_sync_client()
    resp = c.invoices.delete("RO1", "FCT", "0040")
    assert "stearsa" in (resp.message or "")
    req = route.calls[0].request
    assert req.method == "DELETE"
    assert req.url.params["cif"] == "RO1"
    assert req.url.params["seriesName"] == "FCT"
    assert req.url.params["number"] == "0040"
    c.close()


# --- reverse ---
@respx.mock
def test_invoice_reverse_sync():
    route = respx.post(f"{BASE}invoice/reverse").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcResponse", number="0986", series="FFF",
            documentUrl="https://cloud.smartbill.ro/x", documentId="274119",
            documentViewUrl="https://cloud.smartbill.ro/v")))
    c = make_sync_client()
    r = c.invoices.reverse(StornoRequest(company_vat_code="RO1", series_name="FFF", number="0985"))
    assert r.document_id == "274119"
    assert r.document_url.endswith("/x")
    body = route.calls[0].request.read()
    import json
    assert json.loads(body) == {"companyVatCode": "RO1", "seriesName": "FFF", "number": "0985"}
    c.close()


# --- cancel ---
@respx.mock
def test_invoice_cancel_sync():
    route = respx.put(f"{BASE}invoice/cancel").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcResponse", message="Factura cu seria si numarul FCT0040 a fost anulata cu succes.")))
    c = make_sync_client()
    r = c.invoices.cancel("RO1", "FCT", "0040")
    assert "anulata" in (r.message or "")
    assert route.calls[0].request.url.params["seriesName"] == "FCT"
    c.close()


@respx.mock
async def test_invoice_cancel_async():
    respx.put(f"{BASE}invoice/cancel").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", message="ok")))
    ac = make_async_client()
    await ac.invoices.acancel("RO1", "FCT", "0040")
    await ac.aclose()


# --- restore ---
@respx.mock
def test_invoice_restore_sync():
    respx.put(f"{BASE}invoice/restore").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", message="ok")))
    c = make_sync_client()
    c.invoices.restore("RO1", "FCT", "0040")
    c.close()


# --- payment status ---
@respx.mock
def test_invoice_payment_status_sync():
    respx.get(f"{BASE}invoice/paymentstatus").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcInvoicePaymentStatusResponse",
            invoiceTotalAmount=100, paidAmount=62, unpaidAmount=38)))
    c = make_sync_client()
    r = c.invoices.payment_status("RO1", "FCT", "0040")
    assert r.invoice_total_amount == 100
    assert r.paid_amount == 62
    assert r.unpaid_amount == 38
    c.close()


# --- pdf ---
@respx.mock
def test_invoice_pdf_sync():
    route = respx.get(f"{BASE}invoice/pdf").mock(
        return_value=httpx.Response(200, content=b"%PDF-1.4 fake"))
    c = make_sync_client()
    data = c.invoices.pdf("RO1", "FCT", "0040")
    assert data.startswith(b"%PDF")
    assert route.calls[0].request.headers["accept"] == "application/octet-stream"
    c.close()


@respx.mock
async def test_invoice_pdf_async():
    respx.get(f"{BASE}invoice/pdf").mock(
        return_value=httpx.Response(200, content=b"%PDF-1.4 fake"))
    ac = make_async_client()
    data = await ac.invoices.apdf("RO1", "FCT", "0040")
    assert data == b"%PDF-1.4 fake"
    await ac.aclose()


# --- error handling ---
@respx.mock
def test_invoice_create_error_raises():
    respx.post(f"{BASE}invoice").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcResponse", errorText="Client invalid!")))
    c = make_sync_client()
    with pytest.raises(SmartBillAPIError) as ei:
        c.invoices.create(Invoice(company_vat_code="RO1", client=Client(name="x")))
    assert "Client invalid" in ei.value.error_text
    c.close()


@respx.mock
def test_invoice_create_400_raises():
    respx.post(f"{BASE}invoice").mock(
        return_value=httpx.Response(400, json={"Fault": {"errorText": "Date gresite"}}))
    c = make_sync_client()
    with pytest.raises(SmartBillAPIError) as ei:
        c.invoices.create(Invoice(company_vat_code="RO1", client=Client(name="x")))
    assert ei.value.status_code == 400
    c.close()
