from facturify import core


class Empresas(core.Core):
    def get_empresas(
        self,
        /,
        *,
        params: core.Params | None = None,
    ) -> core.Response:
        """
        Listar empresas.

        https://docs.facturify.com/#tag/EmpresasEmisores/operation/listado-emisores
        """
        return self.get(
            'empresa',
            params=params,
        )

    def get_empresa(
        self,
        id: str,
        /,
        *,
        params: core.Params | None = None,
    ) -> core.Response:
        """
        Obtener empresa.

        https://docs.facturify.com/#tag/EmpresasEmisores/operation/informacion-emisor
        """
        return self.get(
            'empresa',
            id,
            params=params,
        )

    def create_empresa(
        self,
        body: core.Body,
        /,
    ) -> core.Response:
        """
        Crear empresa.

        https://docs.facturify.com/#tag/EmpresasEmisores/operation/registrar-emisor
        """
        return self.post(
            body,
            'empresa',
        )

    def update_empresa(
        self,
        id: str,
        body: core.Body,
        /,
    ) -> core.Response:
        """
        Actualizar empresa.

        https://docs.facturify.com/#tag/EmpresasEmisores/operation/actualizar-informacion-fiscal-emisor
        """
        return self.put(
            body,
            'empresa',
            id,
        )
