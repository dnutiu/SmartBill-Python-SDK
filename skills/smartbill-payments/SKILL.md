---
name: smartbill-payments
description: Record payments and issue fiscal receipts (bon fiscal) via SmartBill using smartbill-sdk. POST /payment, payment types, mixed cash/card, fiscal-printer text, delete.
---

# SmartBill Payments & Fiscal Receipts

Record payments against invoices and issue fiscal receipts (`bon fiscal`)
with the `smartbill-sdk` Python package. Sync and async supported.

## Setup

```bash
pip install smartbill-sdk
```

```python
from smartbill_sdk import SmartBillClient
client = SmartBillClient(username="you@example.com", token="...")
```

Auth is HTTP Basic `username:token` (token from SmartBill Cloud →
**Contul Meu → Integrari → API**). JSON only. Rate limit: 30 calls / 10s.

## The payments service

`client.payments` (`PaymentsService`) exposes:

| Method (sync / async)        | Endpoint                  | Purpose                              |
|------------------------------|---------------------------|--------------------------------------|
| `create` / `acreate`         | `POST /payment`           | record a payment / issue bon fiscal  |
| `delete_other` / `adelete_other` | `DELETE /payment/v2`  | delete a non-chitanta payment        |
| `delete_chitanta` / `adelete_chitanta` | `DELETE /payment/chitanta` | delete a chitanta               |
| `fiscal_receipt_text` / `afiscal_receipt_text` | `GET /payment/text` | fetch base64 fiscal-printer text by id |

## Payment types

`Payment.type` is one of (string values, case-sensitive as documented):

`Chitanta`, `Bon`, `Card`, `Card online`, `CEC`, `Bilet ordin`,
`Ordin plata`, `Mandat postal`, `Extras de cont`, `Ramburs`.

(Also available as `from smartbill_sdk.models import PaymentType`.)

## Record a simple payment (chitanta / card / etc.)

```python
from smartbill_sdk.models import Payment

payment = Payment(
    company_vat_code="RO12345678",
    series_name="FCT",            # invoice series the payment applies to
    number="0040",                # invoice number
    value=260.0,
    type="Chitanta",
    payment_date="2026-06-21",    # YYYY-MM-DD
    is_cash=True,
)
resp = client.payments.create(payment)
```

## Issue a fiscal receipt (bon fiscal) with mixed cash + card

A `Bon` is also created via `POST /payment`, but you add `products` and the
`received_*` breakdown. With `return_fiscal_printer_text=True` the response
includes the receipt `id` and the base64 fiscal-printer text in `message`.

```python
from smartbill_sdk.models import Payment, Product

payment = Payment(
    company_vat_code="RO12345678",
    value=260.0,
    type="Bon",
    is_cash=False,
    use_stock=False,
    return_fiscal_printer_text=True,
    products=[
        Product(name="Produs 1", measuring_unit_name="buc", currency="RON",
                quantity=1, price=200, is_tax_included=True,
                tax_name="Normala", tax_percentage=19),
        Product(name="Produs 2", measuring_unit_name="buc", currency="RON",
                quantity=1, price=60, is_tax_included=True,
                tax_name="Normala", tax_percentage=19),
    ],
    received_cash=200.0,
    received_card=60.0,
)
resp = client.payments.create(payment)
print(resp.id)            # generated receipt id
print(resp.message)       # base64 fiscal-printer text (if requested)
```

`create` returns a `FiscalReceiptResponse` (a `BaseResponse` + optional `id`),
so `resp.number`, `resp.series`, `resp.error_text` are also available.

## Fetch fiscal-printer text by id (later)

```python
r = client.payments.fiscal_receipt_text("RO12345678", "12345")
print(r.message)   # base64-encoded text
```

## Delete a payment

```python
# Non-chitanta (uses query params to identify the payment):
client.payments.delete_other(
    "RO12345678",
    payment_type="Card",
    payment_date="2026-06-21",
    payment_value=100.0,
    client_name="Intelligent IT",
    client_cif="RO12345678",
    invoice_series="FCT",
    invoice_number="0040",
)

# Chitanta (identified by its own series + number):
client.payments.delete_chitanta("RO12345678", "CHI", "0001")
```

All `delete_other` kwargs except `payment_type` are optional filters.

## Async

```python
async with AsyncSmartBillClient(username="you@example.com", token="...") as client:
    resp = await client.payments.acreate(payment)
    status = await client.invoices.apayment_status("RO12345678", "FCT", "0040")
```

`acreate`, `adelete_other`, `adelete_chitanta`, `afiscal_receipt_text` mirror
the sync methods. Run concurrent calls with `asyncio.gather(...)`.

## Errors

`SmartBillAPIError` carries `.error_text` (the API's `errorText`),
`.message`, and `.status_code`. See `smartbill_sdk.exceptions`.

## Reference

- Source: `src/smartbill_sdk/services/__init__.py` (`PaymentsService`)
- Models: `src/smartbill_sdk/models/payments.py`, `common.py`,
  `responses.py` (`FiscalReceiptResponse`)
- Worked examples: `examples/create_payment_sync.py`,
  `examples/fiscal_receipt_async.py`
- Spec: `docs/openapi.json`
