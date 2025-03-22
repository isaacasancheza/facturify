from facturify import core
from facturify.clientes import Clientes
from facturify.empresas import Empresas
from facturify.facturas import Facturas
from facturify.token import Token


class Facturify:
    def __init__(
        self,
        access_token: str,
        /,
        *,
        version: core.ApiVersion = 'v1',
        sandbox: bool = False,
    ) -> None:
        self.token = Token(access_token, version=version, sandbox=sandbox)
        self.clientes = Clientes(access_token, version=version, sandbox=sandbox)
        self.facturas = Facturas(access_token, version=version, sandbox=sandbox)
        self.empresas = Empresas(access_token, version=version, sandbox=sandbox)
