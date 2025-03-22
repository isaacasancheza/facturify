from facturify import core


class Facturas(core.Core):
    def get_facturas(
        self,
        params: core.Params | None = None,
    ):
        """
        Listar facturas.

        https://docs.facturify.com/#tag/Facturacion/operation/listado-facturas
        """
        return self.get(
            'factura',
            params=params,
        )

    def get_factura(
        self,
        id: str,
    ):
        """
        Recuperar factura PDF / XML.

        https://docs.facturify.com/#tag/Facturacion/operation/informacion-factura
        """
        return self.get(
            'factura',
            id,
        )

    def create_factura(
        self,
        body: core.Body,
    ):
        """
        Crear factura.

        https://docs.facturify.com/#tag/Facturacion/operation/crear-factura
        """
        return self.post(
            body,
            'factura',
        )

    def cancel_factura(
        self,
        id: str,
    ):
        """
        Cancelar factura.

        https://docs.facturify.com/#tag/Facturacion/operation/cancelar-factura
        """
        return self.put(
            {},
            'factura',
            id,
            'cancel',
        )

    def get_factura_pdf(
        self,
        id: str,
    ):
        """
        Descargar PDF.

        https://docs.facturify.com/#tag/Facturacion/operation/descargar-pdf
        """
        return self.get(
            'factura',
            id,
            'pdf',
        )

    def get_factura_xml(
        self,
        id: str,
    ):
        """
        Descargar XML.

        https://docs.facturify.com/#tag/Facturacion/operation/descargar-xml
        """
        return self.get(
            'factura',
            id,
            'xml',
        )

    def resend_factura(
        self,
        id: str,
        body: dict,
    ):
        """
        En este servicio sé podra hacer un reenvío de PDF y XML de la factura por correo electrónico.

        https://docs.facturify.com/#tag/Facturacion/operation/factura-reenviar-pdf-xml
        """
        return self.put(
            body,
            'factura',
            id,
            'send-email',
        )
