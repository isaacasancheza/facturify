from typing import Literal, TypedDict

from facturify import constants


class WebhookEvent(TypedDict):
    module: constants.WebhookModule
    action: str
    status: str
    data: dict


class WebhookEventFacturaData(TypedDict):
    job_id: str
    xml: str
    pdf: str
    created_at: str
    cfdi_uuid: str
    serie: str
    folio: int
    factura: str


class WebhookEventFactura(TypedDict):
    module: Literal[constants.WebhookModule.INVOICE]
    action: constants.WebhookModuleFacturaAction
    status: constants.WebhookModuleFacturaStatus
    data: WebhookEventFacturaData
