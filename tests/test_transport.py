"""Tests for the transport layer and auth handling (no network)."""

import base64

import httpx
import pytest

from smartbill_sdk import SmartBillClient
from smartbill_sdk._transport import (
    DEFAULT_BASE_URL,
    build_auth,
    build_request,
    handle_response,
    parse_envelope,
)
from smartbill_sdk.exceptions import (
    SmartBillAPIError,
    SmartBillAuthError,
    SmartBillRateLimitError,
)

from conftest import BASE, TOKEN, USERNAME, basic_auth_header


def test_default_base_url():
    assert DEFAULT_BASE_URL == "https://ws.smartbill.ro/SBORO/api/"


def test_build_auth_sets_basic_header():
    header = build_auth(USERNAME, TOKEN)
    expected = "Basic " + base64.b64encode(f"{USERNAME}:{TOKEN}".encode()).decode()
    assert header == expected
    assert header.startswith("Basic ")


def test_build_request_json_headers_and_url():
    req = build_request(
        method="post", base_url=BASE, path="invoice",
        json_body={"invoice": {}}, auth_header=basic_auth_header(),
    )
    assert req.url == "https://ws.smartbill.ro/SBORO/api/invoice"
    assert req.method == "POST"
    assert req.headers["accept"] == "application/json"
    assert req.headers["content-type"] == "application/json"
    assert req.headers["authorization"] == basic_auth_header()


def test_build_request_params():
    req = build_request(method="get", base_url=BASE, path="tax",
                        params={"cif": "RO123"}, auth_header=basic_auth_header())
    assert req.url.params["cif"] == "RO123"


def test_parse_envelope_known_keys():
    assert parse_envelope({"sbcResponse": {"number": "1"}}) == {"number": "1"}
    assert parse_envelope({"Response": {"number": "1"}}) == {"number": "1"}
    assert parse_envelope({"sbcTaxes": {"taxes": []}}) == {"taxes": []}
    assert parse_envelope({"stocks": {"list": []}}) == {"list": []}


def test_parse_envelope_passthrough():
    assert parse_envelope({"number": "1", "series": "FCT"}) == {
        "number": "1", "series": "FCT"
    }
    assert parse_envelope([1, 2, 3]) == [1, 2, 3]


def test_handle_response_401():
    resp = httpx.Response(401, text="nope")
    with pytest.raises(SmartBillAuthError):
        handle_response(resp)


def test_handle_response_403():
    resp = httpx.Response(403, text="blocked")
    with pytest.raises(SmartBillRateLimitError):
        handle_response(resp)


def test_handle_response_error_envelope_raises():
    resp = httpx.Response(200, json={"sbcResponse": {"errorText": "bad"}})
    with pytest.raises(SmartBillAPIError) as ei:
        handle_response(resp)
    assert ei.value.error_text == "bad"
    assert ei.value.status_code == 200


def test_handle_response_success_returns_envelope():
    resp = httpx.Response(200, json={"sbcResponse": {"number": "0010", "series": "FCT"}})
    out = handle_response(resp)
    assert out == {"number": "0010", "series": "FCT"}


def test_handle_response_binary():
    resp = httpx.Response(200, content=b"%PDF-1.4 ...")
    assert handle_response(resp, binary=True) == b"%PDF-1.4 ..."


def test_handle_response_non_2xx_with_body():
    resp = httpx.Response(400, json={"Fault": {"errorText": "Client invalid!"}})
    with pytest.raises(SmartBillAPIError) as ei:
        handle_response(resp)
    assert "Client invalid" in ei.value.error_text
    assert ei.value.status_code == 400


def test_client_sets_services_and_auth():
    c = SmartBillClient(USERNAME, TOKEN, base_url=BASE)
    assert c.invoices is not None
    assert c.taxes is c.series
    assert c.auth_header.startswith("Basic ")
    c.close()
