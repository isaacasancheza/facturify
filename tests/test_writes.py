from datetime import datetime
from os import environ
from time import sleep

import pytest
import requests

from facturify import Facturify

# stamps real CFDIs in the sandbox, which uses up its folios
pytestmark = pytest.mark.skipif(
    'FACTURIFY_SANDBOX_WRITES' not in environ,
    reason='set FACTURIFY_SANDBOX_WRITES to create records in the Facturify sandbox',
)

# SAT test RFC for a sandbox receptor
CLIENTE_RFC = 'EKU9003173C9'


def cliente_body(
    *,
    forma_de_pago: str,
) -> dict[str, str]:
    return {
        'razon_social': 'ESCUELA KEMPER URGATE',
        'rfc': CLIENTE_RFC,
        'email': 'test@example.com',
        'forma_de_pago': forma_de_pago,
        'uso_cfdi': 'G03',
        'cp': '42501',
        'regimen': 'GENERAL DE LEY PERSONAS MORALES',
    }


def test_cliente_lifecycle(
    facturify: Facturify,
) -> None:
    # clientes cannot be deleted, so the test cliente is reused across runs
    clientes = facturify.clientes.get_clientes(
        params={
            'limit': 100,
        },
    )
    existing = [c for c in clientes['data'] if c['rfc'] == CLIENTE_RFC]
    if existing:
        uuid = existing[0]['uuid']
    else:
        response = facturify.clientes.create_cliente(
            cliente_body(
                forma_de_pago='03',
            ),
        )
        uuid = response['data']['uuid']

    current = facturify.clientes.get_cliente(uuid)['data']['forma_de_pago']
    forma_de_pago = '04' if current == '03' else '03'

    response = facturify.clientes.update_cliente(
        uuid,
        cliente_body(
            forma_de_pago=forma_de_pago,
        ),
    )

    assert response['data']['forma_de_pago'] == forma_de_pago
    assert facturify.clientes.get_cliente(uuid)['data']['forma_de_pago'] == (
        forma_de_pago
    )


def test_factura_lifecycle(
    facturify: Facturify,
) -> None:
    emisor = facturify.empresas.get_empresas()['data'][0]
    facturify.empresas.get_empresa(emisor['uuid'])
    now = datetime.now()

    # global factura to the generic RFC, which the sandbox PAC always accepts
    response = facturify.facturas.create_factura(
        {
            'emisor': {
                'uuid': emisor['uuid'],
            },
            'receptor': {
                'razon_social': 'PUBLICO EN GENERAL',
                'rfc': 'XAXX010101000',
                'email': 'test@example.com',
                'regimen': 'SIN OBLIGACIONES FISCALES',
                'cp': emisor['cp'],
                'uso_cfdi': 'S01',
            },
            'factura': {
                'fecha': now.strftime('%Y-%m-%d %H:%M:%S'),
                'tipo': 'ingreso',
                'generacion_automatica': True,
                'version': '4.0',
                'exportacion': '01',
                'metodo_de_pago': 'PUE',
                'forma_de_pago': '03',
                'subtotal': 100,
                'impuesto_federal': 16,
                'total': 116,
                'InformacionGlobal': {
                    'Periodicidad': '04',
                    'Meses': now.strftime('%m'),
                    'Anio': str(now.year),
                },
                'conceptos': [
                    {
                        'clave_producto_servicio': '01010101',
                        'clave_unidad_de_medida': 'ACT',
                        'cantidad': 1,
                        'descripcion': 'PRUEBA FACTURIFY',
                        'valor_unitario': 100,
                        'total': 100,
                        'objeto_imp': '02',
                    },
                ],
            },
        },
    )
    uuid = response['data']['cfdi_uuid']

    # get_factura is left out: the sandbox answers 500 for this factura
    assert facturify.facturas.get_factura_pdf(uuid)['url']
    assert facturify.facturas.get_factura_xml(uuid)['url']
    assert facturify.facturas.resend_factura(
        uuid,
        {
            'emails_send': 'test@example.com',
        },
    )['message']

    # a just-stamped CFDI is rejected with 400 for a few seconds
    for _ in range(12):
        try:
            response = facturify.facturas.cancel_factura(uuid)
            break
        except requests.HTTPError as e:
            if e.response.status_code != 400:
                raise
            sleep(5)
    else:
        pytest.fail(f'factura {uuid} could not be cancelled')

    assert response['success']
