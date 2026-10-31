from facturify import core


class Clientes(core.Core):
    def get_clientes(
        self,
        /,
        *,
        params: core.Params | None = None,
    ) -> core.Response:
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
        /,
    ) -> core.Response:
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
        body: core.Body,
        /,
    ) -> core.Response:
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
        id: str,
        body: core.Body,
        /,
    ) -> core.Response:
        """
        Actualizar cliente.

        https://docs.facturify.com/#tag/ClientesReceptor/operation/actualizar-receptor
        """
        return self.put(
            body,
            'cliente',
            id,
        )
