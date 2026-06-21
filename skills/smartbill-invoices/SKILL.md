---
name: smartbill-invoices
description: Issue and manage SmartBill invoices (and proformas/estimates) via smartbill-sdk. Create, cancel, restore, storno, PDF, payment status — sync and async.
---

# SmartBill Invoices & Estimates

Create, manage, and download SmartBill invoices and proformas (`estimates`)
with the `smartbill-sdk` Python package. Covers sync and async usage.

## Setup

```bash
pip install smartbill-sdk
```

Auth is HTTP Basic with your SmartBill login e-mail and API token
(SmartBill Cloud → **Contul Meu → Integrari → API**).

```python
from smartbill_sdk import SmartBillClient, AsyncSmartBillClient

client = SmartBillClient(username="you@example.com", token="...")
# async:
aclient = AsyncSmartBillClient(username="you@example.com", token="...")
```

All date fields are `YYYY-MM-DD` strings. The SDK sends JSON only (no XML).
SmartBill rate-limits to 30 calls / 10s → 403 for 10 min if exceeded; opt into
a client-side preemptive limiter with `enforce_rate_limit=True`.

## Drafts (ciornă)

Both `Invoice` and `Estimate` accept `is_draft` (API alias `isDraft`). When
`is_draft=True` the document is **saved but not finalized**: it gets **no
series number** and is not officially issued. It shows up in SmartBill Cloud
under **Rapoarte → Facturi / Proforme** so a human can review and finalize it
there. When `is_draft=False` (the default), the document is finalized and a
number is assigned — `resp.series` / `resp.number` are populated.

```python
invoice = Invoice(..., series_name="FCT", is_draft=True, ...)
resp = client.invoices.create(invoice)
# resp.number / resp.series are empty until finalized in SmartBill Cloud
```

## Services available

| Attribute        | Service              | Covers                                       |
|------------------|----------------------|----------------------------------------------|
| `client.invoices`  | `InvoicesService`    | `POST /invoice`, delete, reverse (storno), cancel, restore, payment status, PDF |
| `client.estimates` | `EstimatesService`   | `POST /estimate`, delete, cancel, restore, PDF, invoices-status |
| `client.payments`  | `PaymentsService`    | see the `smartbill-payments` skill           |
| `client.email`     | `EmailService`       | see the `smartbill-email` skill              |
| `client.taxes`     | `ConfigurationService` | `GET /tax` (taxes), `GET /series` (series) |
| `client.stocks`    | `StocksService`      | `GET /stocks`                                |

Note: `client.taxes` and `client.series` are the **same** `ConfigurationService`
instance — call `client.taxes.taxes(cif)` / `client.taxes.series(cif)`.

Sync methods are `foo`; async equivalents are `afoo`
(e.g. `client.invoices.create(...)` vs `await client.invoices.acreate(...)`).

## Create an invoice (sync)

```python
from smartbill_sdk import SmartBillClient
from smartbill_sdk.models import Invoice, Client, Product

with SmartBillClient(username="you@example.com", token="...") as client:
    invoice = Invoice(
        company_vat_code="RO12345678",
        client=Client(name="Intelligent IT", vat_code="RO12345678",
                      city="Sibiu", country="Romania"),
        series_name="FCT",
        is_draft=False,
        products=[
            Product(name="Produs 1", measuring_unit_name="buc", currency="RON",
                    quantity=2, price=10, is_tax_included=True,
                    tax_name="Redusa", tax_percentage=9),
        ],
    )
    resp = client.invoices.create(invoice)
    print(resp.series, resp.number)  # series + assigned number
```

Proformas use `Estimate` + `client.estimates.create(estimate)` — same shape,
and also support `is_draft=True` to save a proforma ciornă.

## Lifecycle: storno / cancel / restore / PDF (sync)

```python
from smartbill_sdk.models import StornoRequest

cif, series, number = "RO12345678", "FCT", "0040"

# Storno (reversal) — returns document URLs.
storno = StornoRequest(company_vat_code=cif, series_name=series, number=number)
st = client.invoices.reverse(storno)
print(st.document_url)

client.invoices.cancel(cif, series, number)     # PUT /invoice/cancel
client.invoices.restore(cif, series, number)    # PUT /invoice/restore

pdf_bytes: bytes = client.invoices.pdf(cif, series, number)  # GET /invoice/pdf
with open("factura.pdf", "wb") as f:
    f.write(pdf_bytes)
```

`pdf()` returns raw `bytes` (binary endpoint — not JSON).

## Payment status of an invoice

```python
status = client.invoices.payment_status(cif, series, number)
print(status.paid, status.invoice_total_amount,
      status.paid_amount, status.unpaid_amount)
```

## Async usage

```python
import asyncio
from smartbill_sdk import AsyncSmartBillClient
from smartbill_sdk.models import Invoice, Client, Product

async def main():
    async with AsyncSmartBillClient(username="you@example.com", token="...") as client:
        invoice = Invoice(
            company_vat_code="RO12345678",
            client=Client(name="X", vat_code="RO1", city="Bucuresti", country="Romania"),
            series_name="FCT", is_draft=False,
            products=[Product(name="P", measuring_unit_name="buc", currency="RON",
                              quantity=1, price=100, is_tax_included=True,
                              tax_name="Normala", tax_percentage=19)],
        )
        resp = await client.invoices.acreate(invoice)
        print(resp.series, resp.number)

asyncio.run(main())
```

Always `await client.aclose()` (or use `async with`) to close the underlying
`httpx.AsyncClient` when you own it.

## Error handling

Errors are `SmartBillError` subclasses from `smartbill_sdk.exceptions`:

- `SmartBillAuthError` — HTTP 401 (bad username/token/company CIF).
- `SmartBillRateLimitError` — HTTP 403 (rate-limited, blocked 10 min).
- `SmartBillAPIError` — has `.error_text`, `.message`, `.status_code`
  (the API's `errorText` is surfaced here).
- `SmartBillTransportError` — network-level failure.

```python
from smartbill_sdk import SmartBillAPIError, SmartBillAuthError
try:
    client.invoices.create(invoice)
except SmartBillAuthError:
    ...
except SmartBillAPIError as e:
    print(e.error_text, e.status_code)
```

## Reference

- Source: `src/smartbill_sdk/services/__init__.py` (`InvoicesService`, `EstimatesService`)
- Models: `src/smartbill_sdk/models/invoices.py`, `estimates.py`, `common.py`
- Worked examples: `examples/create_invoice_sync.py`,
  `examples/create_estimate_sync.py`, `examples/invoice_lifecycle_sync.py`
- Spec: `docs/openapi.json`
