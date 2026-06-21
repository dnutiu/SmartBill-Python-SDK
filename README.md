# smartbill-sdk

A Python SDK for the [SmartBill Cloud REST API](https://www.facturionline.ro/api-program-facturare/),
offering both **synchronous** and **asynchronous** interfaces and typed
request/response models generated from the official `openapi.json` spec.

## Features

- Sync (`SmartBillClient`) and async (`AsyncSmartBillClient`) clients.
- Typed pydantic v2 models for invoices, proformas, payments, emails,
  taxes, series and stocks.
- Covers every endpoint from the SmartBill OpenAPI definition.
- Helper exceptions with the API `errorText` surfaced.

## Installation

```bash
pip install smartbill-sdk
```

From source (development):

```bash
uv sync --extra dev
```

## Authentication

SmartBill uses HTTP Basic Auth with `username:token`:

- `username` — the e-mail you log in with in SmartBill Cloud.
- `token` — found in SmartBill Cloud > **Contul Meu** > **Integrari** > **API**.

```python
from smartbill_sdk import SmartBillClient

client = SmartBillClient(username="you@example.com", token="abc123...")
```

## Quick start (sync)

```python
from smartbill_sdk import SmartBillClient
from smartbill_sdk.models import Invoice, Client, Product

client = SmartBillClient(username="you@example.com", token="...")

invoice = Invoice(
    company_vat_code="RO12345678",
    client=Client(name="Intelligent IT", vat_code="RO12345678", city="Sibiu", country="Romania"),
    series_name="FCT",
    is_draft=False,
    products=[
        Product(name="Produs 1", measuring_unit_name="buc", currency="RON",
                quantity=2, price=10, is_tax_included=True,
                tax_name="Redusa", tax_percentage=9),
    ],
)

resp = client.invoices.create(invoice)
print(resp.series, resp.number)
```

## Quick start (async)

```python
import asyncio
from smartbill_sdk import AsyncSmartBillClient

async def main():
    client = AsyncSmartBillClient(username="you@example.com", token="...")
    taxes = await client.taxes.ataxes("RO12345678")
    print(taxes)
    await client.aclose()

asyncio.run(main())
```

## Endpoints covered

Invoices, Proformas, Payments (incl. chitanta & bon fiscal), E-mail,
Taxes, Series, Stocks. See `smartbill_sdk/services/` for the full list.

## Notes

- The SDK talks JSON by default (`format="json"`); XML is not yet supported.
- Rate limit: the SmartBill API allows 30 calls / 10 seconds. A client-side
  limiter can be enabled with `enforce_rate_limit=True`.
- Date fields use `YYYY-MM-DD` strings, matching the API.

## Disclaimer

This SDK was written by an AI agent (pi) which, to its credit.
The code was generated from the official
`openapi.json` spec, verified with a suite of 63 mocked tests, and refined
until everything passed.

That said, please have a human review it before issuing real invoices —
accountants work hard enough as it is, and the last thing they need is an
enthusiastic model quietly deciding that the 9% reduced rate applies to
shampoo.
