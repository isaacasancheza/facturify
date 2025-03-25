from os import environ

from facturify import Facturify


def test_get_token():
    api_key = environ['API_KEY']
    api_secret = environ['API_SECRET']
    facturify = Facturify('', sandbox=True)
    response = facturify.token.get_token(
        {
            'api_key': api_key,
            'api_secret': api_secret,
        }
    )
    assert response['jwt']['token']
