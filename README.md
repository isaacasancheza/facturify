# facturify

A simple Python wrapper for the [Facturify API](https://docs.facturify.com) (Mexican CFDI invoicing).

## Installation

```sh
uv add git+https://github.com/isaacasancheza/facturify
```

## Usage

```python
from facturify import Facturify

facturify = Facturify(api_token='', sandbox=True)

# Exchange API credentials for a JWT and use it for every resource.
response = facturify.token.get_token(
    {
        'api_key': '...',
        'api_secret': '...',
    },
)
facturify.api_token = response['jwt']['token']

clientes = facturify.clientes.get_clientes()
factura = facturify.facturas.create_factura({...})
pdf = facturify.facturas.get_factura_pdf(factura_uuid)  # {'url': ...}

# When the token expires, refresh it in place.
facturify.api_token = facturify.token.refresh_token()['jwt']['token']
```

Resources: `token`, `clientes`, `empresas` and `facturas`. Each method links to its endpoint in the Facturify docs.

### Options

| Argument | Default | Description |
| --- | --- | --- |
| `sandbox` | `False` | Use `api-sandbox.facturify.com` instead of production. |
| `timeout` | `30` | Request timeout in seconds. |
| `max_retries` | `3` | Retries with exponential backoff (capped at 20s). |
| `retriable_http_codes` | `{429, 500, 502, 503, 504}` | Status codes that trigger a retry. |

GET requests are retried on any retriable code. Writes (POST, PUT, PATCH, DELETE) are retried only on 429, because a write that failed with a 5xx may still have been processed, such as a stamped CFDI.

HTTP errors are raised as `requests.HTTPError`.

### Webhooks

`facturify.typing` and `facturify.constants` provide `TypedDict`s and enums for webhook payloads, e.g. `WebhookEventFactura`.

## Development

```sh
uv sync
uv run ruff format && uv run ruff check
uv run mypy
uv run pytest
```

Sandbox tests are skipped unless `API_KEY` and `API_SECRET` are set. Tests that create clientes and stamp and cancel a CFDI also need `FACTURIFY_SANDBOX_WRITES=1`.
