from os import environ

import pytest

from facturify import Facturify


@pytest.mark.skipif(
    'API_KEY' not in environ or 'API_SECRET' not in environ,
    reason='requires API_KEY and API_SECRET for the Facturify sandbox',
)
def test_get_token() -> None:
    api_key = environ['API_KEY']
    api_secret = environ['API_SECRET']
    facturify = Facturify(api_token='', sandbox=True)
    response = facturify.token.get_token(
        {
            'api_key': api_key,
            'api_secret': api_secret,
        }
    )
    assert response['jwt']['token']
