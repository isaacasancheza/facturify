from os import environ

import pytest

from facturify import Facturify


@pytest.fixture(scope='session')
def facturify() -> Facturify:
    if 'API_KEY' not in environ or 'API_SECRET' not in environ:
        pytest.skip('requires API_KEY and API_SECRET for the Facturify sandbox')

    facturify = Facturify(api_token='', sandbox=True)
    response = facturify.token.get_token(
        {
            'api_key': environ['API_KEY'],
            'api_secret': environ['API_SECRET'],
        },
    )
    facturify.api_token = response['jwt']['token']
    return facturify
