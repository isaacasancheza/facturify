from facturify import core


class Clientes(core.Core):
    def get_clientes(
        self,
        params: core.Params | None = None,
    ):
        """
        Listar clientes.

        https://docs.facturify.com/#tag/ClientesReceptor/operation/listado-receptores
        """
        return self.get(
            'cliente',
            params=params,
        )

    def get_cliente(
        self,
        id: str,
    ):
        """
        Obtener cliente.

        https://docs.facturify.com/#tag/ClientesReceptor/operation/informacion-receptor
        """
        return self.get(
            'cliente',
            id,
        )

    def create_cliente(
        self,
        body: dict,
    ):
        """
        Crear cliente.

        https://docs.facturify.com/#tag/ClientesReceptor/operation/registrar-receptor
        """
        return self.post(
            body,
            'cliente',
        )

    def update_cliente(
        self,
        body: dict,
    ):
        """
        Actualizar cliente.

        https://docs.facturify.com/#tag/ClientesReceptor/operation/actualizar-receptor
        """
        return self.put(
            body,
            'cliente',
        )
