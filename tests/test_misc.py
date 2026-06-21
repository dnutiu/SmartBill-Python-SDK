"""Endpoint tests for email, taxes, series, stocks via respx."""

import json

import httpx
import respx

from smartbill_sdk.models import DocumentType, EmailDocument

from conftest import BASE, envelope, make_sync_client, make_async_client


# --- email ---
@respx.mock
def test_email_send_sync():
    route = respx.post(f"{BASE}document/send").mock(
        return_value=httpx.Response(200, json={
            "Response": {"status": {"code": "0", "message": "Documentul a fost trimis cu succes."}}}))
    c = make_sync_client()
    e = EmailDocument(company_vat_code="RO1", series_name="FCT", number="0040",
                      type=DocumentType.INVOICE, to="office@x.ro",
                      subject="subj", body_text="body")
    r = c.email.send(e)
    assert r.status.code == "0"
    assert "trimis" in r.status.message
    payload = json.loads(route.calls[0].request.read())
    assert payload["sendDocumentRequest"]["companyVatCode"] == "RO1"
    assert payload["sendDocumentRequest"]["type"] == "factura"
    c.close()


@respx.mock
async def test_email_send_async():
    respx.post(f"{BASE}document/send").mock(
        return_value=httpx.Response(200, json={
            "Response": {"status": {"code": 0, "message": "ok"}}}))
    ac = make_async_client()
    e = EmailDocument(company_vat_code="RO1", series_name="FCT", number="0040",
                      type="proforma")
    r = await ac.email.asend(e)
    assert r.status.code == 0
    await ac.aclose()


# --- taxes ---
@respx.mock
def test_taxes_sync():
    route = respx.get(f"{BASE}tax").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcTaxes", taxes=[{"name": "Normala", "percentage": 19},
                               {"name": "Redusa", "percentage": 9}])))
    c = make_sync_client()
    r = c.taxes.taxes("RO1")
    assert len(r.taxes) == 2
    assert r.taxes[0].name == "Normala"
    assert r.taxes[0].percentage == 19
    assert route.calls[0].request.url.params["cif"] == "RO1"
    c.close()


@respx.mock
async def test_taxes_async():
    respx.get(f"{BASE}tax").mock(
        return_value=httpx.Response(200, json=envelope("sbcTaxes", taxes=[])))
    ac = make_async_client()
    r = await ac.taxes.ataxes("RO1")
    assert r.taxes == []
    await ac.aclose()


# --- series ---
@respx.mock
def test_series_sync_with_type():
    route = respx.get(f"{BASE}series").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcSeries", list=[{"name": "FCT", "nextNumber": "0117", "type": "f"},
                               {"name": "CHT", "nextNumber": 13, "type": "c"}])))
    c = make_sync_client()
    r = c.series.series("RO1", type="f")
    assert len(r.list) == 2
    assert r.list[0].name == "FCT"
    assert r.list[0].next_number == "0117"
    assert r.list[1].next_number == 13
    p = route.calls[0].request.url.params
    assert p["cif"] == "RO1"
    assert p["type"] == "f"
    c.close()


@respx.mock
def test_series_sync_without_type():
    route = respx.get(f"{BASE}series").mock(
        return_value=httpx.Response(200, json=envelope("sbcSeries", list=[])))
    c = make_sync_client()
    c.series.series("RO1")
    assert "type" not in route.calls[0].request.url.params
    c.close()


@respx.mock
async def test_series_async():
    respx.get(f"{BASE}series").mock(
        return_value=httpx.Response(200, json=envelope("sbcSeries", list=[])))
    ac = make_async_client()
    await ac.series.aseries("RO1")
    await ac.aclose()


# --- stocks ---
@respx.mock
def test_stocks_sync():
    route = respx.get(f"{BASE}stocks").mock(
        return_value=httpx.Response(200, json={
            "stocks": {
                "errorText": "", "message": "", "number": "", "series": "",
                "list": [
                    {"products": [{"measuringUnit": "buc", "productCode": "IT001",
                                   "productName": "Revista IT", "quantity": 100}],
                     "warehouse": {"warehouseName": "GestiuneMagazin1", "warehouseType": "en detail"}},
                ],
            }}))
    c = make_sync_client()
    r = c.stocks.get("RO1", "2021-03-01", warehouse_name="Depozit")
    assert len(r.list) == 1
    assert r.list[0].products[0].product_name == "Revista IT"
    assert r.list[0].warehouse.warehouse_type == "en detail"
    p = route.calls[0].request.url.params
    assert p["cif"] == "RO1"
    assert p["date"] == "2021-03-01"
    assert p["warehouseName"] == "Depozit"
    c.close()


@respx.mock
async def test_stocks_async():
    respx.get(f"{BASE}stocks").mock(
        return_value=httpx.Response(200, json={
            "stocks": {"list": []}}))
    ac = make_async_client()
    r = await ac.stocks.aget("RO1", "2021-03-01", product_name="X", product_code="Y")
    assert r.list == []
    await ac.aclose()


@respx.mock
def test_stocks_error_envelope_raises():
    import pytest
    from smartbill_sdk import SmartBillAPIError
    respx.get(f"{BASE}stocks").mock(
        return_value=httpx.Response(200, json={
            "stocks": {"errorText": "Data la care vreti sa aflati valoarea stocului trebuie specificata!"}})
    )
    c = make_sync_client()
    with pytest.raises(SmartBillAPIError) as ei:
        c.stocks.get("RO1", "2021-03-01")
    assert "Data" in ei.value.error_text
    c.close()
