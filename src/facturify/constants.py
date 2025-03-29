from enum import StrEnum


class WebhookModule(StrEnum):
    INVOICE = 'invoice'


class WebhookModuleFacturaAction(StrEnum):
    STAMP = 'STAMP'
    CANCELLATION = 'CANCELLATION'


class WebhookModuleFacturaStatus(StrEnum):
    ERROR = 'ERROR'
    TIMBRADO = 'TIMBRADO'
    CANCELADO = 'CANCELADO'
