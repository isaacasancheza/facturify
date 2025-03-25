from dataclasses import dataclass
from typing import cast


@dataclass
class Error:
    code: int
    field: str
    message: str


class NotFoundError(Exception):
    def __init__(self, response: dict) -> None:
        super().__init__()
        self.code = cast(int, response['code'])
        self.message = cast(str, response['message'])


class UnauthorizerdError(Exception):
    def __init__(self, response: dict) -> None:
        super().__init__()
        self.code = cast(int, response.get('code', ''))
        self.message = cast(str, response.get('message', ''))


class UnprocessableEntityError(Exception):
    def __init__(self, response: dict) -> None:
        super().__init__()
        self.code = cast(int, response['code'])
        self.message = cast(str, response['message'])
        self.errors = [Error(**error) for error in response['errors']]
