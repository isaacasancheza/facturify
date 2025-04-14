from abc import ABC
from time import sleep
from typing import Any, Callable, Literal, NotRequired, TypedDict, Unpack

import requests

type URL = str | int
type Body = dict
type Params = dict
type Method = Literal['GET', 'PUT', 'POST', 'PATCH', 'DELETE']
type Headers = dict

SANDBOX_URL = 'https://api-sandbox.facturify.com/api'
PRODUCTION_URL = 'https://api.facturify.com/api'


class OptionalArguments(TypedDict):
    params: NotRequired[Params | None]
    headers: NotRequired[Headers | None]
    ignore_auth: NotRequired[bool | None]


class Core(ABC):
    def __init__(
        self,
        api_token: str | Callable[[], str],
        /,
        *,
        version: Literal['v1'] = 'v1',
        sandbox: bool = False,
        max_retries: int = 3,
        retriable_http_codes: set[int] = {401 | 429 | 500 | 502 | 503 | 504},
    ) -> None:
        self._api_root = (SANDBOX_URL if sandbox else PRODUCTION_URL) + f'/{version}/'
        self._api_token = api_token
        self._max_retries = max_retries
        self._retriable_http_codes = retriable_http_codes

    def get(
        self,
        /,
        *args: URL,
        **kwargs: Unpack[OptionalArguments],
    ):
        return self.wrapper(
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
        return self.wrapper(
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
        return self.wrapper(
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
        return self.wrapper(
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
        return self.wrapper(
            *args,
            **kwargs,
            body=data,
            method='DELETE',
        )

    def wrapper(
        self,
        *args: URL,
        body: Body | None = None,
        params: Params | None = None,
        method: Method,
        headers: Headers | None = None,
        ignore_auth: bool | None = False,
    ) -> dict[str, Any]:
        retries = 0
        exception = None
        while retries < self._max_retries:
            try:
                return self.request(
                    *args,
                    body=body,
                    params=params,
                    method=method,
                    headers=headers,
                    ignore_auth=ignore_auth,
                )
            except Exception as e:
                exception = e
                if (
                    isinstance(e, requests.HTTPError)
                    and e.response.status_code in self._retriable_http_codes
                ):
                    backoff = min(2**retries, 20)
                    sleep(backoff)
                    retries += 1
                    continue
                raise
        raise (exception if exception else RuntimeError('Exception should be thrown'))

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
            api_token = (
                self._api_token
                if isinstance(self._api_token, str)
                else self._api_token()
            )
            headers['Authorization'] = f'Bearer {api_token}'

        url = self._api_root + '/'.join(str(arg) for arg in args)

        response = requests.request(
            url=url,
            data=body,
            method=method,
            params=params,
            headers=headers,
        )

        response.raise_for_status()

        return response.json()
