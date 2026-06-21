---
name: smartbill-email
description: Send SmartBill documents (invoices/proformas) by email via smartbill-sdk. POST /document/send, base64 subject/body, sync and async.
---

# SmartBill Email (document/send)

Email an existing SmartBill invoice or proforma to recipients using the
`smartbill-sdk` Python package. Sync and async supported.

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

## The email service

`client.email` (`EmailService`) exposes:

| Method (sync / async) | Endpoint            | Purpose                       |
|-----------------------|---------------------|-------------------------------|
| `send` / `asend`      | `POST /document/send` | email a document to recipients |

## ⚠️ Base64 requirement

The SmartBill API requires `subject` and `body_text` to be **Base64-encoded**
by the caller. The SDK does **not** do this for you — encode before passing:

```python
import base64

def b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")
```

## Send an invoice (sync)

```python
import base64
from smartbill_sdk import SmartBillClient
from smartbill_sdk.models import DocumentType, EmailDocument

def b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")

with SmartBillClient(username="you@example.com", token="...") as client:
    email = EmailDocument(
        company_vat_code="RO12345678",
        series_name="FCT",
        number="0040",
        type=DocumentType.INVOICE,        # or DocumentType.PROFORMA
        to="client@example.ro",
        cc="contabilitate@example.ro",
        # bcc="secret@example.ro",
        subject=b64("Factura FCT0040"),
        body_text=b64("Vă trimitem factura FCT0040. Mulțumim!"),
    )
    resp = client.email.send(email)
    print(resp.status.code, resp.status.message)   # "0" == success
```

`type` selects which document to send: `DocumentType.INVOICE` (`"factura"`)
or `DocumentType.PROFORMA` (`"proforma"`). The document is identified by
`series_name` + `number` + `type` + `company_vat_code`.

## Send a proforma (async)

```python
import asyncio, base64
from smartbill_sdk import AsyncSmartBillClient
from smartbill_sdk.models import DocumentType, EmailDocument

def b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")

async def main():
    async with AsyncSmartBillClient(username="you@example.com", token="...") as client:
        email = EmailDocument(
            company_vat_code="RO12345678",
            series_name="PFC",
            number="0001",
            type=DocumentType.PROFORMA,
            to="client@example.ro",
            subject=b64("Proforma PFC0001"),
            body_text=b64("Vă trimitem proforma PFC0001."),
        )
        resp = await client.email.asend(email)
        print(resp.status.code, resp.status.message)

asyncio.run(main())
```

## Response

`send` returns an `EmailResponse` whose `status` is an `EmailStatus` with
`code` (`"0"` on success) and `message`.

## Errors

`SmartBillAPIError` carries `.error_text` (the API's `errorText`),
`.message`, and `.status_code`. See `smartbill_sdk.exceptions`.

## Reference

- Source: `src/smartbill_sdk/services/__init__.py` (`EmailService`)
- Models: `src/smartbill_sdk/models/email.py`, `responses.py` (`EmailResponse`),
  `common.py` (`DocumentType`)
- Worked example: `examples/send_email_sync.py`
- Spec: `docs/openapi.json`
