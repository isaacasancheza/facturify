# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Thin Python wrapper around the [Facturify](https://docs.facturify.com) REST API (Mexican CFDI invoicing). Python ≥3.13, managed with `uv`, built with hatchling. Only runtime dependency is `requests`. The API's OpenAPI spec is at https://docs.facturify.com/es/compiled.yaml (the docs page itself is a JS-rendered ReDoc shell).

## Commands

```sh
uv sync                                   # install deps (incl. dev group)
uv run --no-sync ruff format src tests    # format
uv run --no-sync ruff check src tests     # lint
uv run --no-sync mypy                     # type check (strict, src + tests)
uv run --no-sync pytest                   # run tests
uv run --no-sync pytest tests/test_core.py::test_sends_body_as_json   # single test
```

Ruff and mypy are configured in `pyproject.toml`. The project ruff config replaces any user-level one, so it carries the single-quote style and the `__init__.py` F401 ignore itself.

`tests/test_core.py` contains unit tests that swap the client's `requests.Session` for a fake and stub out `core.sleep`. The other test modules hit the real sandbox through the `facturify` fixture in `tests/conftest.py`, which skips unless `API_KEY` and `API_SECRET` are set (sandbox values live in SSM at `/facturify/sandbox/api-key` and `/facturify/sandbox/api-secret`). `tests/test_writes.py` also needs `FACTURIFY_SANDBOX_WRITES=1`, since it stamps and cancels a real sandbox CFDI.

Sandbox quirks the tests work around: listing facturas requires `page`, `limit`, `from` and `to`; the SAT test receptor RFCs are rejected at stamping (`CFDI40147`), so facturas go to `XAXX010101000` with `InformacionGlobal`; cancelling a just-stamped CFDI returns 400 `SAT: UUID No existe` until SAT registers it (seconds to minutes), and too many cancel attempts lock that CFDI out with `Alcanzo máximo de solicitudes para cancelación`, so retry sparingly; payment complements (`tipo: 'pago'`) are created with `create_factura` and go to the same generic receptor, with Facturify stamping `Moneda` as `XXX`; `get_factura` returns 500 for those facturas; identical concurrent requests get `409 Solicitud duplicada en proceso`.

## Architecture

- `core.Client` (`src/facturify/core.py`) holds all shared state: base URL (sandbox vs production plus API `version`), the bearer token (`api_token`, mutable), retry settings, timeout and one `requests.Session`. All HTTP goes through `Client.wrapper` (retry loop with exponential backoff capped at 20s) → `Client.request` (joins positional path segments with `/`, adds `Authorization: Bearer` unless `ignore_auth=True`, sends the body as JSON, `raise_for_status()`, returns `response.json()`).
- Retry rule: GET is retried on any code in `retriable_http_codes`; other methods only on 429, because a failed write may already have been processed (e.g. a stamped CFDI). 401 is not retried by default.
- `core.Core` is the base for resource classes (`Token`, `Clientes`, `Empresas`, `Facturas`). It takes the shared `Client` and exposes `get`/`post`/`put`/`patch`/`delete`. Write verbs take the body as the first positional argument, except `delete`, which takes it as `body=`. Each resource method passes path segments positionally (e.g. `self.put(body, 'factura', id, 'cancel')`), returns `core.Response`, and has a Spanish docstring linking to the matching docs.facturify.com operation. Follow this pattern when adding endpoints.
- `Facturify` (`src/facturify/facturify.py`) is the public entry point (re-exported from `__init__.py`). It builds one `Client`, passes it to every resource (`facturify.facturas`, `facturify.clientes`, …), and exposes an `api_token` property for swapping the token after `token.refresh_token()`. A new constructor option must be added to both `Facturify.__init__` and `Client.__init__`; a new resource class must be wired in here.
- `constants.py` (StrEnums) and `typing.py` (TypedDicts) describe incoming webhook event payloads; they are not used by the HTTP client itself.
- The package ships `py.typed`. Request bodies, params and responses are plain `dict`s (no models/dataclasses).

## Conventions

- Domain naming is Spanish (`clientes`, `empresas`, `facturas`, `timbrado`), matching the Facturify API resource names.
- Prefix commit messages with the gitmoji emoji character (e.g. 🐛, ✨, ♻️), not the `:shortcode:` form used in older history.
