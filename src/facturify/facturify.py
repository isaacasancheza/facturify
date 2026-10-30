from typing import Literal

from facturify.clientes import Clientes
from facturify.core import Client
from facturify.empresas import Empresas
from facturify.facturas import Facturas
from facturify.token import Token


class Facturify:
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
        self._client = Client(
            api_token=api_token,
            version=version,
            sandbox=sandbox,
            max_retries=max_retries,
            retriable_http_codes=retriable_http_codes,
            timeout=timeout,
        )
        self.token = Token(self._client)
        self.clientes = Clientes(self._client)
        self.facturas = Facturas(self._client)
        self.empresas = Empresas(self._client)

    @property
    def api_token(
        self,
        /,
    ) -> str:
        return self._client.api_token

    @api_token.setter
    def api_token(
        self,
        api_token: str,
        /,
    ) -> None:
        """
        Reemplaza el token usado por todos los recursos, p. ej. tras `token.refresh_token()`.
        """
        self._client.api_token = api_token
