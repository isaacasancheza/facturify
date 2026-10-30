from datetime import date, timedelta
from os import environ
from typing import Any

import pytest

from facturify import Facturify

pytestmark = pytest.mark.skipif(
    'API_KEY' not in environ or 'API_SECRET' not in environ,
    reason='requires API_KEY and API_SECRET for the Facturify sandbox',
)


@pytest.fixture(scope='module')
def facturify() -> Facturify:
    facturify = Facturify(api_token='', sandbox=True)
    response = facturify.token.get_token(
        {
            'api_key': environ['API_KEY'],
            'api_secret': environ['API_SECRET'],
        },
    )
    facturify.api_token = response['jwt']['token']
    return facturify


def test_get_token(
    facturify: Facturify,
) -> None:
    assert facturify.api_token


def test_validate_token(
    facturify: Facturify,
) -> None:
    facturify.token.validate_token()


def test_refresh_token(
    facturify: Facturify,
) -> None:
    response = facturify.token.refresh_token()
    facturify.api_token = response['jwt']['token']

    facturify.token.validate_token()


@pytest.mark.parametrize(
    'resource, method, params',
    [
        ('clientes', 'get_clientes', None),
        ('empresas', 'get_empresas', None),
        (
            'facturas',
            'get_facturas',
            {
                'page': 1,
                'limit': 10,
                'from': (date.today() - timedelta(days=30)).isoformat(),
                'to': date.today().isoformat(),
            },
        ),
    ],
)
def test_list_resources(
    facturify: Facturify,
    resource: str,
    method: str,
    params: dict[str, Any] | None,
) -> None:
    response = getattr(getattr(facturify, resource), method)(params=params)

    assert isinstance(response, dict)
