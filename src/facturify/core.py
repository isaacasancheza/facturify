from abc import ABC
from time import sleep
from typing import Any, Literal, NotRequired, TypedDict, Unpack

import requests

type URL = str | int
type Body = dict[str, Any]
type Params = dict[str, Any]
type Method = Literal['GET', 'PUT', 'POST', 'PATCH', 'DELETE']
type Headers = dict[str, str]
type Response = dict[str, Any]

SANDBOX_URL = 'https://api-sandbox.facturify.com/api'
PRODUCTION_URL = 'https://api.facturify.com/api'

DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRIABLE_HTTP_CODES = {429, 500, 502, 503, 504}
DEFAULT_TIMEOUT = 30.0

# A failed write may still have been processed (e.g. a stamped CFDI), so only
# these methods are retried on every retriable code; others only on 429.
IDEMPOTENT_METHODS = {'GET'}
TOO_MANY_REQUESTS = 429


class OptionalArguments(TypedDict):
    params: NotRequired[Params | None]
    headers: NotRequired[Headers | None]
    ignore_auth: NotRequired[bool]


class Client:
    def __init__(
        self,
        *,
        api_token: str,
        version: Literal['v1'] = 'v1',
        sandbox: bool = False,
        max_retries: int | None = None,
        retriable_http_codes: set[int] | None = None,
        timeout: float | None = None,
    ) -> None:
        self.api_token = api_token
        self._api_root = (SANDBOX_URL if sandbox else PRODUCTION_URL) + f'/{version}/'
        self._max_retries = (
            max_retries if max_retries is not None else DEFAULT_MAX_RETRIES
        )
        self._retriable_http_codes = (
            retriable_http_codes
            if retriable_http_codes is not None
            else DEFAULT_RETRIABLE_HTTP_CODES
        )
        self._timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self._session = requests.Session()

    def _is_retriable(
        self,
        *,
        method: Method,
        status_code: int,
    ) -> bool:
        if status_code not in self._retriable_http_codes:
            return False
        return method in IDEMPOTENT_METHODS or status_code == TOO_MANY_REQUESTS

    def wrapper(
        self,
        *args: URL,
        body: Body | None = None,
        params: Params | None = None,
        method: Method,
        headers: Headers | None = None,
        ignore_auth: bool = False,
    ) -> Response:
        retries = 0
        exception = None
        while retries <= self._max_retries:
            try:
                return self.request(
                    *args,
                    body=body,
                    params=params,
                    method=method,
                    headers=headers,
                    ignore_auth=ignore_auth,
                )
            except requests.HTTPError as e:
                exception = e
                if self._is_retriable(
                    method=method,
                    status_code=e.response.status_code,
                ):
                    backoff = min(2**retries, 20)
                    sleep(backoff)
                    retries += 1
                    continue
                raise
        raise (
            exception
            if exception
            else RuntimeError('An exception should have been thrown')
        )

    def request(
        self,
        *args: URL,
        body: Body | None = None,
        params: Params | None = None,
        method: Method,
        headers: Headers | None = None,
        ignore_auth: bool = False,
    ) -> Response:
        headers = {**(headers or {})}
        if not ignore_auth:
            headers['Authorization'] = f'Bearer {self.api_token}'

        url = self._api_root + '/'.join(str(arg) for arg in args)

        response = self._session.request(
            url=url,
            json=body,
            method=method,
            params=params,
            headers=headers,
            timeout=self._timeout,
        )

        response.raise_for_status()

        data: Response = response.json()
        return data


class Core(ABC):
    def __init__(
        self,
        client: Client,
        /,
    ) -> None:
        self._client = client

    def get(
        self,
        /,
        *args: URL,
        **kwargs: Unpack[OptionalArguments],
    ) -> Response:
        return self._client.wrapper(
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
    ) -> Response:
        return self._client.wrapper(
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
    ) -> Response:
        return self._client.wrapper(
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
    ) -> Response:
        return self._client.wrapper(
            *args,
            **kwargs,
            body=body,
            method='PATCH',
        )

    def delete(
        self,
        /,
        *args: URL,
        body: Body | None = None,
        **kwargs: Unpack[OptionalArguments],
    ) -> Response:
        return self._client.wrapper(
            *args,
            **kwargs,
            body=body,
            method='DELETE',
        )
