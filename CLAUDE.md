# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Thin Python wrapper around the [Facturify](https://docs.facturify.com) REST API (Mexican CFDI invoicing). Python ≥3.13, managed with `uv`, built with hatchling. Only runtime dependency is `requests`.

## Commands

```sh
uv sync                                   # install deps (incl. dev group)
uv run --no-sync ruff format src tests    # format
uv run --no-sync ruff check src tests     # lint
uv run --no-sync mypy src                 # type check
uv run --no-sync pytest                   # run tests
uv run --no-sync pytest tests/test_token.py::test_get_token   # single test
```

There is no ruff config in `pyproject.toml`; formatting (single quotes) comes from the user-level `~/.config/ruff/ruff.toml`.

Tests hit the real Facturify **sandbox** API and require `API_KEY` and `API_SECRET` environment variables.

## Architecture

- `core.Core` (`src/facturify/core.py`) is the base for every resource class. It holds the base URL (sandbox vs production, plus API `version`), the bearer token, and retry settings. All HTTP goes through `get`/`post`/`put`/`patch`/`delete` → `wrapper` (retry loop with exponential backoff, capped at 20s, on `retriable_http_codes`; default includes 401/429/5xx) → `request` (builds the URL by joining positional path segments with `/`, adds the `Authorization: Bearer` header unless `ignore_auth=True`, calls `raise_for_status()`, returns `response.json()`).
- Resource classes (`Token`, `Clientes`, `Empresas`, `Facturas`) each subclass `Core` and expose one method per endpoint. Methods pass path segments positionally (e.g. `self.put(body, 'factura', id, 'cancel')`), take the body as the first positional arg for write verbs, and carry a Spanish docstring linking to the matching docs.facturify.com operation. Follow this pattern when adding endpoints.
- `Facturify` (`src/facturify/facturify.py`) is the public entry point (re-exported from `__init__.py`). It instantiates each resource class with the same constructor kwargs and exposes them as attributes (`facturify.facturas`, `facturify.clientes`, …). A new constructor option must be added to both `Core.__init__` and `Facturify.__init__` and forwarded to every resource; a new resource class must be wired in here.
- `constants.py` (StrEnums) and `typing.py` (TypedDicts) describe incoming webhook event payloads; they are not used by the HTTP client itself.

Request bodies and params are plain `dict`s (no models/dataclasses). Note that `request` sends the body via `data=` (form-encoded), not `json=`.

## Conventions

- Domain naming is Spanish (`clientes`, `empresas`, `facturas`, `timbrado`), matching the Facturify API resource names.
- Prefix commit messages with the gitmoji emoji character (e.g. 🐛, ✨, ♻️), not the `:shortcode:` form used in older history.
