# PROJECT KNOWLEDGE BASE

**Generated:** 2026-06-21

## OVERVIEW
Project: **smartbill-sdk**
Stack: Python ≥ 3.11, `httpx>=0.27`, `pydantic>=2.6`; build backend `hatchling`; dependency/
dev env managed with `uv`; tests with `pytest` + `pytest-asyncio` + `respx`.

A Python SDK for the [SmartBill Cloud REST API](https://www.facturionline.ro/api-program-facturare/)
offering both **synchronous** (`SmartBillClient`) and **asynchronous**
(`AsyncSmartBillClient`) interfaces, with typed pydantic v2 request/response
models covering every endpoint in the official `docs/openapi.json` spec.

## STRUCTURE
```
src/smartbill_sdk/      # the package (src-layout)
  __init__.py           # public API + __all__ re-exports
  client.py             # SmartBillClient (sync)
  async_client.py       # AsyncSmartBillClient (async)
  _transport.py         # shared request build / auth / envelope unwrap / errors / RateLimiter
  exceptions.py         # SmartBillError hierarchy
  models/               # pydantic v2 models per resource (alias camelCase <-> snake_case)
  services/             # per-resource endpoint logic, shared by sync + async clients
tests/                  # pytest suite, mocked via respx (63 tests)
examples/               # standalone runnable example scripts
docs/openapi.json       # official SmartBill OpenAPI spec (source of truth)
pyproject.toml          # project + hatch build + pytest config
uv.lock                 # lockfile
```
*   `src/smartbill_sdk/services/__init__.py`: All endpoint logic. Each service builds
    `httpx.Request` objects and defines both sync (`create`, `delete`, ...) and async
    (`acreate`, `adelete`, ...) methods that delegate to an injected `_Executor`
    (`execute` / `aexecute`). Defined once, used by both clients.
*   `src/smartbill_sdk/_transport.py`: Auth (HTTP Basic `username:token`), request
    construction, SmartBill response-envelope unwrapping, error mapping, and the
    optional client-side `RateLimiter` (SmartBill enforces 30 calls / 10s, then 403
    for 10 minutes).
*   `src/smartbill_sdk/models/`: snake_case attrs aliased to camelCase JSON; models
    are permissive (`extra="allow"`) so new API fields don't break parsing.

## COMMANDS
| Action              | Command                          |
|---------------------|----------------------------------|
| Install (dev)       | `uv sync --extra dev`            |
| Run tests           | `uv run pytest` (or `uv run pytest -q`) |
| Run a single test   | `uv run pytest tests/test_invoices.py` |
| Build wheel         | `uv build`                       |
| Run an example      | `uv run python examples/create_invoice_sync.py` |

Note: `pytest-asyncio` runs in `asyncio_mode = "auto"` (see `pyproject.toml`), so
async test functions need no `@pytest.mark.asyncio` decorator.

## CODING STANDARDS
*   **Language**: Python 3.11+ (`from __future__ import annotations` is used throughout).
*   **Style**: 4-space indent, double-quote strings, module-level docstrings, full
    type hints, `Optional[...]` over `| None`. No formatter/linter is currently
    configured (no ruff/black/mypy in `pyproject.toml`) — match the existing style.
*   **Models**: pydantic v2, subclass the `ModelConfig` base in `models/common.py`
    (`populate_by_name=True`, `extra="allow"`). Use `Field(..., alias="camelCase")`
    and `AliasChoices` for snake_case ⇄ camelCase mapping. Serialize with
    `model_dump(by_alias=True, exclude_none=True)`.
*   **Services**: keep sync + async methods paired in the same service class; sync
    method `foo` → async `afoo`. Build the `httpx.Request` once in a private
    `_foo_request(...)` helper, then both `foo` and `afoo` reuse it.
*   **Errors**: raise `SmartBillError` subclasses from `exceptions.py`; never bare
    `Exception`. `handle_response()` in `_transport.py` is the single place that
    maps HTTP status / envelopes to exceptions.
*   **Responses**: the SmartBill API wraps payloads in envelopes (`sbcResponse`,
    `Response`, `sbcTaxes`, `sbcSeries`, `sbcInvoicePaymentStatusResponse`,
    `stocks`, `Fault`). `parse_envelope()` unwraps them — don't unwrap manually.

## WHERE TO LOOK
*   **Source**: `src/smartbill_sdk/`
*   **Tests**: `tests/` (mocked HTTP via `respx`; `tests/conftest.py` has shared
    fixtures/helpers like `make_sync_client`, `make_async_client`, `envelope()`)
*   **Docs**: `README.md`, `docs/openapi.json` (official spec), `examples/`
*   **Public API surface**: `src/smartbill_sdk/__init__.py` (`__all__`)

## NOTES
*   **Auth**: SmartBill uses HTTP Basic Auth with `username:token` where `username`
    is the login e-mail and `token` comes from SmartBill Cloud → *Contul Meu →
    Integrari → API*.
*   **JSON only**: the SDK sends JSON (`format="json"`); XML is not supported.
*   **Rate limit**: 30 calls / 10 seconds — exceeding it triggers a server-side 403
    that blocks access for 10 minutes. Opt into a client-side preemptive limiter with
    `SmartBillClient(..., enforce_rate_limit=True)`.
*   **Dates**: all date fields are `YYYY-MM-DD` strings, matching the API.
*   **Sync vs async**: `SmartBillClient` exposes sync service methods (`client.invoices.create`)
    and `AsyncSmartBillClient` exposes async ones (`await client.invoices.acreate`).
    Calling the wrong one raises a clear `SmartBillError`.
*   **`taxes` / `series` alias**: on both clients, `client.taxes` and `client.series`
    are the *same* `ConfigurationService` instance (taxes + series share one service).
*   **Tests are mocked**: no network calls; `respx` intercepts `httpx`. The full suite
    (63 tests) passes offline.
*   **Disclaimer (from README)**: the SDK was AI-generated from `openapi.json` and
    verified with 63 mocked tests — please have a human review before issuing real
    invoices.
*   No other context files (`.cursorrules`, `CLAUDE.md`, etc.) were found in the repo.
