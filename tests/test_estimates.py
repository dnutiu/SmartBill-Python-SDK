"""Endpoint tests for EstimatesService via respx."""

import json

import httpx
import respx

from smartbill_sdk.models import Client, Estimate, Product

from conftest import (
    BASE,
    assert_auth,
    envelope,
    make_async_client,
    make_sync_client,
)


@respx.mock
def test_estimate_create_sync():
    route = respx.post(f"{BASE}estimate").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcResponse", number="0001", series="PFC")))
    c = make_sync_client()
    est = Estimate(company_vat_code="RO1", client=Client(name="X"),
                   series_name="PFC", products=[Product(name="p", measuring_unit_name="buc",
                                                        currency="RON", quantity=1, price=10)])
    r = c.estimates.create(est)
    assert r.series == "PFC"
    assert r.number == "0001"
    payload = json.loads(route.calls[0].request.read())
    assert payload["companyVatCode"] == "RO1"
    assert_auth(route.calls[0].request)
    c.close()


@respx.mock
async def test_estimate_create_async():
    respx.post(f"{BASE}estimate").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", number="2", series="PFC")))
    ac = make_async_client()
    r = await ac.estimates.acreate(Estimate(company_vat_code="RO1", client=Client(name="X"), products=[]))
    assert r.number == "2"
    await ac.aclose()


@respx.mock
def test_estimate_delete_sync():
    route = respx.delete(f"{BASE}estimate").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", message="ok")))
    c = make_sync_client()
    c.estimates.delete("RO1", "PFC", "0001")
    assert route.calls[0].request.url.params["seriesName"] == "PFC"
    c.close()


@respx.mock
def test_estimate_cancel_sync():
    route = respx.put(f"{BASE}estimate/cancel").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", message="ok")))
    c = make_sync_client()
    c.estimates.cancel("RO1", "PFC", "0001")
    assert route.calls[0].request.url.params["number"] == "0001"
    c.close()


@respx.mock
def test_estimate_restore_sync():
    respx.put(f"{BASE}estimate/restore").mock(
        return_value=httpx.Response(200, json=envelope("sbcResponse", message="ok")))
    c = make_sync_client()
    c.estimates.restore("RO1", "PFC", "0001")
    c.close()


@respx.mock
def test_estimate_pdf_sync():
    route = respx.get(f"{BASE}estimate/pdf").mock(
        return_value=httpx.Response(200, content=b"%PDF-1.4 pf"))
    c = make_sync_client()
    data = c.estimates.pdf("RO1", "PFC", "0001")
    assert data == b"%PDF-1.4 pf"
    assert route.calls[0].request.headers["accept"] == "application/octet-stream"
    c.close()


@respx.mock
def test_estimate_invoices_status_sync():
    respx.get(f"{BASE}estimate/invoices").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcResponse",
            areInvoicesCreated=True,
            invoices=[{"series": "FCT", "number": "0028"},
                      {"series": "FCT", "number": "0036"}])))
    c = make_sync_client()
    r = c.estimates.invoices_status("RO1", "PFC", "0001")
    assert r.are_invoices_created is True
    assert len(r.invoices) == 2
    assert r.invoices[0].series_name == "FCT"
    c.close()


@respx.mock
async def test_estimate_invoices_status_async():
    respx.get(f"{BASE}estimate/invoices").mock(
        return_value=httpx.Response(200, json=envelope(
            "sbcResponse", areInvoicesCreated=False, invoices=[])))
    ac = make_async_client()
    r = await ac.estimates.ainvoices_status("RO1", "PFC", "0001")
    assert r.are_invoices_created is False
    await ac.aclose()
