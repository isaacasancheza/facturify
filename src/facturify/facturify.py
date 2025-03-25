from typing import Callable, Literal

from facturify.clientes import Clientes
from facturify.empresas import Empresas
from facturify.facturas import Facturas
from facturify.token import Token


class Facturify:
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
        self.token = Token(
            api_token,
            version=version,
            sandbox=sandbox,
            max_retries=max_retries,
            retriable_http_codes=retriable_http_codes,
        )
        self.clientes = Clientes(
            api_token,
            version=version,
            sandbox=sandbox,
            max_retries=max_retries,
            retriable_http_codes=retriable_http_codes,
        )
        self.facturas = Facturas(
            api_token,
            version=version,
            sandbox=sandbox,
            max_retries=max_retries,
            retriable_http_codes=retriable_http_codes,
        )
        self.empresas = Empresas(
            api_token,
            version=version,
            sandbox=sandbox,
            max_retries=max_retries,
            retriable_http_codes=retriable_http_codes,
        )
