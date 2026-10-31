from base64 import b64decode
from datetime import datetime
from os import environ
from time import sleep
from typing import Any
from xml.etree import ElementTree

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


def publico_en_general(
    emisor: dict[str, Any],
    /,
    *,
    uso_cfdi: str,
) -> dict[str, Any]:
    # the generic RFC, which the sandbox PAC accepts unlike the SAT test RFCs
    return {
        'razon_social': 'PUBLICO EN GENERAL',
        'rfc': 'XAXX010101000',
        'email': 'test@example.com',
        'regimen': 'SIN OBLIGACIONES FISCALES',
        'cp': emisor['cp'],
        'uso_cfdi': uso_cfdi,
    }


def create_ingreso(
    facturify: Facturify,
    emisor: dict[str, Any],
    /,
    *,
    metodo_de_pago: str,
    forma_de_pago: str,
) -> dict[str, Any]:
    """
    Global factura de ingreso for $100 plus 16% IVA.
    """
    now = datetime.now()
    response = facturify.facturas.create_factura(
        {
            'emisor': {
                'uuid': emisor['uuid'],
            },
            'receptor': publico_en_general(
                emisor,
                uso_cfdi='S01',
            ),
            'factura': {
                'fecha': now.strftime('%Y-%m-%d %H:%M:%S'),
                'tipo': 'ingreso',
                'generacion_automatica': True,
                'version': '4.0',
                'exportacion': '01',
                'metodo_de_pago': metodo_de_pago,
                'forma_de_pago': forma_de_pago,
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
    data: dict[str, Any] = response['data']
    return data


def create_pago(
    facturify: Facturify,
    emisor: dict[str, Any],
    ingreso: dict[str, Any],
    /,
    *,
    parcialidad: int,
    saldo_anterior: float,
) -> dict[str, Any]:
    """
    Complemento de pago (Pagos 2.0) for a $58 installment, $50 plus 16% IVA.
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    traslado = {
        'Base': 50,
        'Impuesto': '002',
        'TipoFactor': 'Tasa',
        'TasaOCuota': '0.160000',
        'Importe': 8,
    }
    response = facturify.facturas.create_factura(
        {
            'emisor': {
                'uuid': emisor['uuid'],
            },
            'receptor': publico_en_general(
                emisor,
                uso_cfdi='CP01',
            ),
            'factura': {
                'fecha': now,
                'tipo': 'pago',
                'generacion_automatica': True,
                'version': '4.0',
                'exportacion': '01',
                'forma_de_pago': '03',
                # Facturify stamps the comprobante with Moneda XXX
                'moneda': 'MXN',
                'tipo_de_cambio': 1,
                'subtotal': 0,
                'impuesto_federal': 0,
                'total': 0,
                'conceptos': [
                    {
                        'cantidad': 1,
                        'clave_producto_servicio': '84111506',
                        'clave_unidad_de_medida': 'ACT',
                        'descripcion': 'Pago',
                        'valor_unitario': 0,
                        'subtotal': 0,
                        'total': 0,
                        'objeto_imp': '01',
                    },
                ],
                'pagos': [
                    {
                        'fecha': now,
                        'forma_de_pago': '03',
                        'moneda': 'MXN',
                        'tipo_de_cambio': 1,
                        'monto': 58,
                        'ImpuestosP': {
                            'TrasladosP': {
                                'TrasladoP': [
                                    {f'{k}P': v for k, v in traslado.items()},
                                ],
                            },
                        },
                        'documento_relacionado': [
                            {
                                'id_documento': ingreso['cfdi_uuid'],
                                'serie': ingreso['serie'],
                                'folio': ingreso['folio'],
                                'moneda': 'MXN',
                                'metodo_de_pago': 'PPD',
                                'numero_de_parcialidad': parcialidad,
                                'importe_saldo_anterior': saldo_anterior,
                                'importe_pagado': 58,
                                'importe_saldo_insoluto': saldo_anterior - 58,
                                'objeto_imp_dr': '02',
                                'ImpuestosDR': {
                                    'TrasladosDR': {
                                        'TrasladoDR': [
                                            {f'{k}DR': v for k, v in traslado.items()},
                                        ],
                                    },
                                },
                            },
                        ],
                    },
                ],
            },
        },
    )
    data: dict[str, Any] = response['data']
    return data


def xml_attributes(
    factura: dict[str, Any],
    tag: str,
    /,
) -> dict[str, str]:
    root = ElementTree.fromstring(b64decode(factura['xml']))
    for element in root.iter():
        if element.tag.rpartition('}')[2] == tag:
            return dict(element.attrib)
    raise AssertionError(f'{tag} not found')


def test_factura_lifecycle(
    facturify: Facturify,
) -> None:
    emisor = facturify.empresas.get_empresas()['data'][0]
    facturify.empresas.get_empresa(emisor['uuid'])

    uuid = create_ingreso(
        facturify,
        emisor,
        metodo_de_pago='PUE',
        forma_de_pago='03',
    )['cfdi_uuid']

    # get_factura is left out: the sandbox answers 500 for this factura
    assert facturify.facturas.get_factura_pdf(uuid)['url']
    assert facturify.facturas.get_factura_xml(uuid)['url']
    assert facturify.facturas.resend_factura(
        uuid,
        {
            'emails_send': 'test@example.com',
        },
    )['message']

    # SAT answers 400 "UUID No existe" until it registers a just-stamped CFDI,
    # and too many cancellation requests lock the CFDI out, so retry sparingly
    for _ in range(8):
        try:
            response = facturify.facturas.cancel_factura(uuid)
            break
        except requests.HTTPError as e:
            if e.response.status_code != 400 or 'No existe' not in e.response.text:
                raise
            sleep(15)
    else:
        pytest.fail(f'factura {uuid} could not be cancelled')

    assert response['success']


def test_complemento_de_pago(
    facturify: Facturify,
) -> None:
    emisor = facturify.empresas.get_empresas()['data'][0]

    # $116 paid later, in two installments of $58
    ingreso = create_ingreso(
        facturify,
        emisor,
        metodo_de_pago='PPD',
        forma_de_pago='99',
    )
    primero = create_pago(
        facturify,
        emisor,
        ingreso,
        parcialidad=1,
        saldo_anterior=116,
    )
    segundo = create_pago(
        facturify,
        emisor,
        ingreso,
        parcialidad=2,
        saldo_anterior=58,
    )

    assert xml_attributes(ingreso, 'Comprobante')['MetodoPago'] == 'PPD'
    for pago, parcialidad, saldo_insoluto in [
        (primero, '1', '58.00'),
        (segundo, '2', '0.00'),
    ]:
        comprobante = xml_attributes(pago, 'Comprobante')
        assert comprobante['TipoDeComprobante'] == 'P'
        assert comprobante['Moneda'] == 'XXX'
        assert xml_attributes(pago, 'Totales')['MontoTotalPagos'] == '58'

        documento = xml_attributes(pago, 'DoctoRelacionado')
        assert documento['IdDocumento'] == ingreso['cfdi_uuid']
        assert documento['NumParcialidad'] == parcialidad
        assert documento['ImpPagado'] == '58.00'
        assert documento['ImpSaldoInsoluto'] == saldo_insoluto

    # left active: SAT takes minutes to register new CFDIs for cancellation
