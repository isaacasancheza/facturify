from facturify import core


class Token(core.Core):
    def get_token(
        self,
        body: dict,
    ):
        """
        Obtener token.

        https://docs.facturify.com/#tag/Token/operation/obtener-token
        """
        return self.post(
            body,
            'auth',
            ignore_auth=True,
        )

    def validate_token(
        self,
    ):
        """
        Validar token.

        https://docs.facturify.com/#tag/Token/operation/validar-token
        """
        return self.get(
            'token',
            'validate',
        )

    def refresh_token(
        self,
    ):
        """
        Refrescar token.

        https://docs.facturify.com/#tag/Token/operation/refrescar-token
        """
        return self.post(
            {},
            'token',
            'refresh',
        )
