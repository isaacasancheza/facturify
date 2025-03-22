from facturify import core


class Token(core.Core):
    def get_token(
        self,
        body: dict,
    ):
        return self.post(
            body,
            'auth',
            ignore_auth=True,
        )

    def validate_token(
        self,
    ):
        return self.get(
            'token',
            'validate',
        )

    def refresh_token(
        self,
    ):
        return self.post(
            {},
            'token',
            'refresh',
        )
