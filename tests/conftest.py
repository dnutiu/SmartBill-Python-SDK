"""Shared test helpers."""

import base64

import httpx
import respx

from smartbill_sdk import AsyncSmartBillClient, SmartBillClient

BASE = "https://ws.smartbill.ro/SBORO/api/"
USERNAME = "user@example.com"
TOKEN = "tok123"


def basic_auth_header() -> str:
    return "Basic " + base64.b64encode(f"{USERNAME}:{TOKEN}".encode()).decode()


def make_sync_client(**kw) -> SmartBillClient:
    return SmartBillClient(USERNAME, TOKEN, base_url=BASE, **kw)


def make_async_client(**kw) -> AsyncSmartBillClient:
    return AsyncSmartBillClient(USERNAME, TOKEN, base_url=BASE, **kw)


def assert_auth(req: httpx.Request) -> None:
    assert req.headers["authorization"] == basic_auth_header()


def assert_json_headers(req: httpx.Request) -> None:
    assert req.headers["accept"] == "application/json"
    assert req.headers["content-type"] == "application/json"


def envelope(key: str, **fields):
    """Build a SmartBill-style response envelope."""
    return {key: fields}
