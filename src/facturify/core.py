from abc import ABC
from typing import Any, Literal, NotRequired, TypedDict, Unpack

import requests

from facturify import exceptions

type URL = str | int
type Body = dict
type Params = dict
type Method = Literal['GET', 'PUT', 'POST', 'PATCH', 'DELETE']
type Headers = dict
type ApiVersion = Literal['v1']

SANDBOX_URL = 'https://api-sandbox.facturify.com/api'
PRODUCTION_URL = 'https://api.facturify.com/api'


class OptionalArguments(TypedDict):
    params: NotRequired[Params | None]
    headers: NotRequired[Headers | None]
    ignore_auth: NotRequired[bool | None]


class Core(ABC):
    def __init__(
        self,
        access_token: str,
        /,
        *,
        version: ApiVersion = 'v1',
        sandbox: bool = False,
    ) -> None:
        self._api_root = (SANDBOX_URL if sandbox else PRODUCTION_URL) + f'/{version}/'
        self._access_token = access_token

    def get(
        self,
        /,
        *args: URL,
        **kwargs: Unpack[OptionalArguments],
    ):
        return self.request(
            *args,
            **kwargs,
            method='GET',
        )

    def put(
        self,
        body: Body,
        /,
        *args: URL,
        **kwargs: Unpack[OptionalArguments],
    ):
        return self.request(
            *args,
            **kwargs,
            body=body,
            method='PUT',
        )

    def post(
        self,
        body: Body,
        /,
        *args: URL,
        **kwargs: Unpack[OptionalArguments],
    ):
        return self.request(
            *args,
            **kwargs,
            body=body,
            method='POST',
        )

    def patch(
        self,
        body: Body,
        /,
        *args: URL,
        **kwargs: Unpack[OptionalArguments],
    ):
        return self.request(
            *args,
            **kwargs,
            body=body,
            method='PATCH',
        )

    def delete(
        self,
        /,
        data: Body | None = None,
        *args: URL,
        **kwargs: Unpack[OptionalArguments],
    ):
        return self.request(
            *args,
            **kwargs,
            body=data,
            method='DELETE',
        )

    def request(
        self,
        *args: URL,
        body: Body | None = None,
        params: Params | None = None,
        method: Method,
        headers: Headers | None = None,
        ignore_auth: bool | None = False,
    ) -> dict[str, Any]:
        if not ignore_auth:
            if not headers:
                headers = {}
            headers['Authorization'] = f'Bearer {self._access_token}'

        url = self._api_root + '/'.join(str(arg) for arg in args)

        response = requests.request(
            url=url,
            data=body,
            method=method,
            params=params,
            headers=headers,
        )

        data = response.json()

        if response.ok:
            return data

        match response.status_code:
            case 401:
                raise exceptions.UnauthorizerdError(data)
            case 404:
                raise exceptions.NotFoundError(data)
            case 422:
                raise exceptions.UnprocessableEntityError(data)

        response.raise_for_status()
        raise
