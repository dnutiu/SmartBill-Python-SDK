# Changelog

All notable changes to this project are documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-06-21

First stable release of the Python SDK for the SmartBill Cloud REST API.

### Added
- Synchronous `SmartBillClient` and asynchronous `AsyncSmartBillClient` with
  HTTP Basic (`username:token`) authentication.
- Typed pydantic v2 request/response models for every endpoint in the official
  `docs/openapi.json` spec, using snake_case attributes aliased to the
  camelCase JSON field names.
- Per-resource services covering invoices, proformas (estimates), payments
  (incl. `chitanta` and `bon fiscal`), e-mail, taxes, series and stocks.
- Exception hierarchy (`SmartBillError`, `SmartBillAuthError`,
  `SmartBillRateLimitError`, `SmartBillAPIError`, `SmartBillTransportError`)
  that surfaces the API `errorText`.
- SmartBill response-envelope unwrapping (`sbcResponse`, `Response`,
  `sbcTaxes`, `sbcSeries`, `sbcInvoicePaymentStatusResponse`, `stocks`,
  `Fault`) centralized in `_transport.parse_envelope`.
- Optional client-side `RateLimiter` (`enforce_rate_limit=True`) to preempt
  the server's 403 (SmartBill blocks access for 10 minutes after >30 calls
  in 10 seconds).
- Binary PDF retrieval for invoices, proformas and fiscal receipts.
- Draft (ciornă) support via `is_draft=True` on `Invoice`, `Estimate` and
  `Payment`.
- Runnable example scripts under `examples/` and copy-pasteable pi agent
  skills under `skills/` (`smartbill-invoices`, `smartbill-payments`,
  `smartbill-email`).
- Test suite of 63 mocked tests using `respx` (no network calls).

### Fixed
- **Critical:** request bodies were incorrectly wrapped in XML-style
  envelopes (`{"invoice": {...}}`, `{"estimate": {...}}`, `{"payment": {...}}`,
  `{"sendDocumentRequest": {...}}`). The JSON endpoints reject these with
  `400 Unrecognized property: <envelope>.` Envelope wrapping has been removed
  from all POST request builders in `services/__init__.py`; the request body
  is now the bare model. Verified against the live SmartBill API by emitting
  a draft invoice.
- `InvoiceRef.series_name` now accepts both `seriesName` (requests) and
  `series` (the `GET /estimate/invoices` response) via `AliasChoices`, while
  still serializing as `seriesName`.
- `PaymentsService.create` / `acreate` now return `FiscalReceiptResponse`
  (exposes the generated receipt `id`) instead of `BaseResponse`.
- README quick-start example used the non-existent `client.taxes.list(...)`;
  corrected to `client.taxes.ataxes(...)`.

### Notes
- The SDK sends JSON only (`format="json"`); XML is not supported.
- Date fields use `YYYY-MM-DD` strings, matching the API.
- This SDK was AI-generated from the official `openapi.json` spec and
  verified with a suite of mocked tests, then refined against live API
  calls. Please have a human review before issuing real invoices.
