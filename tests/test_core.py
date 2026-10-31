import json
from typing import Any

import pytest
import requests

from facturify import Facturify, core


class FakeSession:
    def __init__(
        self,
        *statuses: int,
    ) -> None:
        self.statuses = list(statuses)
        self.calls: list[dict[str, Any]] = []

    def request(
        self,
        **kwargs: Any,
    ) -> requests.Response:
        self.calls.append(kwargs)
        response = requests.Response()
        response.status_code = self.statuses.pop(0)
        response.url = kwargs['url']
        response._content = json.dumps(
            {
                'ok': True,
            },
        ).encode()
        return response


def make_facturify(
    monkeypatch: pytest.MonkeyPatch,
    /,
    *statuses: int,
    **kwargs: Any,
) -> tuple[Facturify, FakeSession]:
    facturify = Facturify(
        **{
            'api_token': 'token',
            'sandbox': True,
            **kwargs,
        },
    )
    session = FakeSession(*statuses)
    monkeypatch.setattr(facturify._client, '_session', session)
    monkeypatch.setattr(core, 'sleep', lambda _: None)
    return facturify, session


def test_builds_url_and_sends_auth_header(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 200)

    assert facturify.facturas.get_factura_pdf('abc') == {
        'ok': True,
    }

    [call] = session.calls
    assert call['method'] == 'GET'
    assert call['url'] == f'{core.SANDBOX_URL}/v1/factura/abc/pdf'
    assert call['headers'] == {
        'Authorization': 'Bearer token',
    }


def test_production_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 200, sandbox=False)

    facturify.clientes.get_clientes()

    assert session.calls[0]['url'] == f'{core.PRODUCTION_URL}/v1/cliente'


def test_sends_body_as_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 200)
    body = {
        'conceptos': [
            {
                'cantidad': 1,
            },
        ],
    }

    facturify.facturas.create_factura(body)

    [call] = session.calls
    assert call['json'] == body
    assert 'data' not in call


def test_ignore_auth_omits_header(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 200)

    facturify.token.get_token(
        {
            'api_key': 'key',
        },
    )

    assert 'Authorization' not in session.calls[0]['headers']


def test_does_not_mutate_caller_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 200)
    headers = {
        'X-Custom': 'value',
    }

    facturify.facturas.get(
        'factura',
        headers=headers,
    )

    assert headers == {
        'X-Custom': 'value',
    }
    assert session.calls[0]['headers'] == {
        'X-Custom': 'value',
        'Authorization': 'Bearer token',
    }


def test_default_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 200)

    facturify.facturas.get_facturas()

    assert session.calls[0]['timeout'] == core.DEFAULT_TIMEOUT


def test_custom_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 200, timeout=5)

    facturify.facturas.get_facturas()

    assert session.calls[0]['timeout'] == 5


def test_retries_get_on_server_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 503, 502, 200)

    assert facturify.facturas.get_facturas() == {
        'ok': True,
    }
    assert len(session.calls) == 3


def test_does_not_retry_post_on_server_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 500, 200)

    with pytest.raises(requests.HTTPError):
        facturify.facturas.create_factura(
            {
                'serie': 'A',
            },
        )
    assert len(session.calls) == 1


def test_retries_post_on_rate_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 429, 200)

    facturify.facturas.create_factura(
        {
            'serie': 'A',
        },
    )
    assert len(session.calls) == 2


def test_does_not_retry_unauthorized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 401, 200)

    with pytest.raises(requests.HTTPError):
        facturify.token.validate_token()
    assert len(session.calls) == 1


def test_raises_after_max_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 503, 503, 503, max_retries=2)

    with pytest.raises(requests.HTTPError):
        facturify.facturas.get_facturas()
    assert len(session.calls) == 3


def test_api_token_update_applies_to_all_resources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 200, 200)

    facturify.api_token = 'refreshed'
    facturify.clientes.get_clientes()
    facturify.empresas.get_empresas()

    assert facturify.api_token == 'refreshed'
    assert [call['headers']['Authorization'] for call in session.calls] == [
        'Bearer refreshed',
        'Bearer refreshed',
    ]


def test_delete_takes_path_positionally_and_body_by_keyword(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 200)

    facturify.facturas.delete(
        'factura',
        'abc',
        body={
            'motivo': '02',
        },
    )

    [call] = session.calls
    assert call['method'] == 'DELETE'
    assert call['url'] == f'{core.SANDBOX_URL}/v1/factura/abc'
    assert call['json'] == {
        'motivo': '02',
    }


def test_resend_factura_posts_to_send_mail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facturify, session = make_facturify(monkeypatch, 200)

    facturify.facturas.resend_factura(
        'abc',
        {
            'emails_send': 'test@example.com',
        },
    )

    [call] = session.calls
    assert call['method'] == 'POST'
    assert call['url'] == f'{core.SANDBOX_URL}/v1/factura/abc/send-mail'
