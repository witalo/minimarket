import decimal
import html

import requests
from django.db.models import Max
from django.http import JsonResponse
from http import HTTPStatus
from .models import *
import math
from django.contrib.auth.models import User
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from django.db import DatabaseError, IntegrityError
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt


def query_dni(document, type_document):
    url = 'https://www.facturacionelectronica.us/facturacion/controller/ws_consulta_rucdni_v2.php'
    _user_marvisur = '20498189637'
    _pw_marvisur = 'marvisur.123.'
    _user_nikitus = '10465240861'
    _pw_nikitus = '123456.'
    params = {
        'usuario': _user_marvisur,
        'password': _pw_marvisur,
        'documento': type_document,
        'nro_documento': document
    }
    r = requests.get(url, params)

    if r.status_code == 200:
        result = r.json()
        if result.get('success') == "True":
            context = {
                'success': result.get('success'),
                'statusMessage': result.get('statusMessage'),
                'result': result.get('result'),
                'DNI': result.get('result').get('DNI'),
                'Nombre': result.get('result').get('Nombre'),
                'Paterno': result.get('result').get('Paterno'),
                'Materno': result.get('result').get('Materno'),
                'RazonSocial': result.get('result').get('RazonSocial'),
                'Direccion': result.get('result').get('Direccion'),
                'FechaNac': result.get('result').get('FechaNac')
            }
        else:
            context = {
                'success': result.get('success'),
                'statusMessage': result.get('statusMessage'),
                'result': result.get('result'),
            }
    else:
        result = r.json()
        context = {
            'errors': result.get("errors"),
            'codigo': result.get("codigo"),
        }
    return context


def query_api_free_ruc(nro_ruc, type_document):
    context = {}
    if type_document == 'RUC':
        url = 'https://dniruc.apisperu.com/api/v1/ruc/{}'.format(nro_ruc)
        params = {
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Im1nbC5zdWFyZXoxQGdtYWlsLmNvbSJ9.JAdBpBl_qWivPcmVnEBfUlng8-TbNJZeoWmtVlHRooI',
        }
        r = requests.get(url, params)

        if r.status_code == 200:
            result = r.json()
            if len(result) < 5:
                context = {
                    'ruc': '',
                    'razonSocial': '',
                    'direccion': '',
                }
            else:
                context = {
                    'ruc': result.get('ruc'),
                    'razonSocial': html.unescape(result.get('razonSocial')),
                    'direccion': html.unescape(result.get('direccion')),
                }

        elif r.status_code == 400:
            context = {
                'status': False,
                'ruc': None,
                'errors': '400 Bad Request',
            }
    return context


def query_api_free_dni(nro_dni, type_document):
    context = {}
    if type_document == 'DNI':
        url = 'https://dni.optimizeperu.com/api/prod/persons/{}'.format(nro_dni)
        headers = {
            'authorization': 'token 48b5594ab9a37a8c3581e5e71ed89c7538a36f11',
        }
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            result = r.json()
            if result == {}:
                context = {
                    'status': False,
                    'DNI': '',
                    'Nombre': '',
                    'Paterno': '',
                    'Materno': '',
                }
            else:
                context = {
                    'status': True,
                    'DNI': result.get('dni'),
                    'Nombre': html.unescape(result.get('name')),
                    'Paterno': html.unescape(result.get('first_name')),
                    'Materno': html.unescape(result.get('last_name')),
                }

        else:
            result = r.json()
            context = {
                'status': False,
                'errors': '400 Bad Request',
            }
    return context


def get_bill_correlative(serial, type):
    value_bill = 1
    order_bill_set = OrderBill.objects.filter(serial=serial, type=type).aggregate(Max('number_receipt'))
    if order_bill_set['number_receipt__max']:
        value_bill = value_bill + order_bill_set['number_receipt__max']
        return value_bill
    else:
        return value_bill


def send_f_nubefact(pk, serial):
    global total_perceptron, total_with_perceptron
    order_obj = Order.objects.get(id=int(pk))
    n_receipt = get_bill_correlative(serial, '1')
    details = OrderDetail.objects.filter(order=order_obj)
    client_obj = order_obj.client
    register_date = order_obj.create_at
    formatdate = register_date.strftime("%d-%m-%Y")

    items = []
    index = 1
    sub_total = 0
    total = 0
    igv_total = 0
    for d in details:
        base_total = d.quantity_sold * d.price_unit  # 5 * 20 = 100
        base_amount = base_total / decimal.Decimal(1.1800)  # 100 / 1.18 = 84.75
        igv = base_total - base_amount  # 100 - 84.75 = 15.25
        sub_total = sub_total + base_amount
        total = total + base_total
        igv_total = igv_total + igv
        total_perceptron = (total * 2) / 100
        total_with_perceptron = total + total_perceptron
        item = {
            "item": index,  # index para los detalles
            "unidad_de_medida": 'NIU',  # NIU viene del nubefact NIU=PRODUCTO
            "codigo": "001",  # codigo del producto opcional
            "codigo_producto_sunat": "10000000",  # codigo del producto excel-sunat
            "descripcion": d.product.names,
            "cantidad": float(round(d.quantity, 2)),
            "valor_unitario": float(round((base_amount / d.quantity), 2)),  # valor unitario sin IGV
            "precio_unitario": float(round(d.price_unit, 2)),
            "descuento": "",
            "subtotal": float(round(base_amount, 2)),  # resultado del valor unitario por la cantidad menos el descuento
            "tipo_de_igv": 1,  # operacion onerosa
            "igv": float(round(igv, 2)),
            "total": float(round(base_total, 2)),
            "anticipo_regularizacion": 'false',
            "anticipo_documento_serie": "",
            "anticipo_documento_numero": "",
        }
        items.append(item)
        index = index + 1

    params = {
        "operacion": "generar_comprobante",
        "tipo_de_comprobante": 1,
        "serie": serial,
        "numero": n_receipt,
        "sunat_transaction": 15,
        "cliente_tipo_de_documento": 6,
        "cliente_numero_de_documento": client_obj.document,
        "cliente_denominacion": client_obj.full_names,
        "cliente_direccion": client_obj.address,
        "cliente_email": client_obj.email,
        "cliente_email_1": "",
        "cliente_email_2": "",
        "fecha_de_emision": formatdate,
        "fecha_de_vencimiento": "",
        "moneda": 1,
        "tipo_de_cambio": "",
        "porcentaje_de_igv": 18.00,
        "descuento_global": "",
        "total_descuento": "",
        "total_anticipo": "",
        "total_gravada": float(round(sub_total, 2)),
        "total_inafecta": "",
        "total_exonerada": "",
        "total_igv": float(round(igv_total, 2)),
        "total_gratuita": "",
        "total_otros_cargos": "",
        "total": float(round(total, 2)),
        "percepcion_tipo": 1,
        "percepcion_base_imponible": float(round(total, 2)),
        "total_percepcion": float(round(total_perceptron, 2)),
        "total_incluido_percepcion": float(round(total_with_perceptron, 2)),
        "total_impuestos_bolsas": "",
        "detraccion": 'false',
        "observaciones": "",
        "documento_que_se_modifica_tipo": "",
        "documento_que_se_modifica_serie": "",
        "documento_que_se_modifica_numero": "",
        "tipo_de_nota_de_credito": "",
        "tipo_de_nota_de_debito": "",
        "enviar_automaticamente_a_la_sunat": 'true',
        "enviar_automaticamente_al_cliente": 'false',
        "condiciones_de_pago": "",
        "medio_de_pago": "",
        "placa_vehiculo": "",
        "orden_compra_servicio": "",
        "formato_de_pdf": "",
        "generado_por_contingencia": "",
        "bienes_region_selva": "",
        "servicios_region_selva": "",
        "items": items,
    }
    _url = 'https://www.pse.pe/api/v1/91900d0da6424013b4cf9a8c4fdf8846b67addc7bbcb41328e137a9c93479e26'
    _authorization = 'eyJhbGciOiJIUzI1NiJ9.IjY1NTJmNDE1NGZhOTQ5ZGU4MjFjYTIwYmE4ZWM4ZDg1MzAxMDRlZmNlNGNjNDcyMGI0ZDU2MGE5ZGQwOGNhMmQi.GNzvsfMsCITQ-xwfK-yl_TQwcLd4F-264wYK19frMXE'
    url = _url
    headers = {
        "Authorization": _authorization,
        "Content-Type": 'application/json'
    }
    response = requests.post(url, json=params, headers=headers)

    if response.status_code == 200:
        result = response.json()
        context = {
            'tipo_de_comprobante': result.get("tipo_de_comprobante"),
            'serie': result.get("serie"),
            'numero': result.get("numero"),
            'aceptada_por_sunat': result.get("aceptada_por_sunat"),
            'sunat_description': result.get("sunat_description"),
            'enlace_del_pdf': result.get("enlace_del_pdf"),
            'cadena_para_codigo_qr': result.get("cadena_para_codigo_qr"),
            'codigo_hash': result.get("codigo_hash"),
            'params': params
        }
    else:
        result = response.json()
        context = {
            'errors': result.get("errors"),
            'codigo': result.get("codigo"),
        }
    return context


def send_b_nubefact(pk, serial):
    order_obj = Order.objects.get(id=int(pk))
    n_receipt = get_bill_correlative(serial, '2')
    details = OrderDetail.objects.filter(order=order_obj)
    client_obj = order_obj.client
    register_date = order_obj.create_at
    formatdate = register_date.strftime("%d-%m-%Y")
    items = []
    index = 1
    sub_total = 0
    total = 0
    igv_total = 0
    for d in details:
        base_total = d.quantity_sold * d.price_unit  # 5 * 20 = 100
        base_amount = base_total / decimal.Decimal(1.1800)  # 100 / 1.18 = 84.75
        igv = base_total - base_amount  # 100 - 84.75 = 15.25
        sub_total = sub_total + base_amount
        total = total + base_total
        igv_total = igv_total + igv
        item = {
            "item": index,  # index para los detalles
            "unidad_de_medida": 'NIU',  # NIU viene del nubefact NIU=PRODUCTO
            "codigo": "001",  # codigo del producto opcional
            "codigo_producto_sunat": "10000000",  # codigo del producto excel-sunat
            "descripcion": d.product.names,
            "cantidad": float(round(d.quantity, 2)),
            "valor_unitario": float(round((base_amount / d.quantity), 2)),  # valor unitario sin IGV
            "precio_unitario": float(round(d.price_unit, 2)),
            "descuento": "",
            "subtotal": float(round(base_amount, 2)),  # resultado del valor unitario por la cantidad menos el descuento
            "tipo_de_igv": 1,  # operacion onerosa
            "igv": float(round(igv, 2)),
            "total": float(round(base_total, 2)),
            "anticipo_regularizacion": 'false',
            "anticipo_documento_serie": "",
            "anticipo_documento_numero": "",
        }
        items.append(item)
        index = index + 1

    params = {
        "operacion": "generar_comprobante",
        "tipo_de_comprobante": 2,
        "serie": serial,
        "numero": n_receipt,
        "sunat_transaction": 1,
        "cliente_tipo_de_documento": 1,  # cambiar cuando este bien
        "cliente_numero_de_documento": client_obj.document,
        "cliente_denominacion": client_obj.full_names,
        "cliente_direccion": client_obj.address,
        "cliente_email": client_obj.email,
        "cliente_email_1": "",
        "cliente_email_2": "",
        "fecha_de_emision": formatdate,
        "fecha_de_vencimiento": "",
        "moneda": 1,
        "tipo_de_cambio": "",
        "porcentaje_de_igv": 18.00,
        "descuento_global": "",
        "total_descuento": "",
        "total_anticipo": "",
        "total_gravada": float(round(sub_total, 2)),
        "total_inafecta": "",
        "total_exonerada": "",
        "total_igv": float(round(igv_total, 2)),
        "total_gratuita": "",
        "total_otros_cargos": "",
        "total": float(round(total, 2)),
        "percepcion_tipo": "",
        "percepcion_base_imponible": "",
        "total_percepcion": "",
        "total_incluido_percepcion": "",
        "total_impuestos_bolsas": "",
        "detraccion": 'false',
        "observaciones": "",
        "documento_que_se_modifica_tipo": "",
        "documento_que_se_modifica_serie": "",
        "documento_que_se_modifica_numero": "",
        "tipo_de_nota_de_credito": "",
        "tipo_de_nota_de_debito": "",
        "enviar_automaticamente_a_la_sunat": 'true',
        "enviar_automaticamente_al_cliente": 'false',
        "codigo_unico": "",
        "condiciones_de_pago": "",
        "medio_de_pago": "",
        "placa_vehiculo": "",
        "orden_compra_servicio": "",
        "tabla_personalizada_codigo": "",
        "formato_de_pdf": "",
        "items": items,
    }
    _url = 'https://www.pse.pe/api/v1/91900d0da6424013b4cf9a8c4fdf8846b67addc7bbcb41328e137a9c93479e26'
    _authorization = 'eyJhbGciOiJIUzI1NiJ9.IjY1NTJmNDE1NGZhOTQ5ZGU4MjFjYTIwYmE4ZWM4ZDg1MzAxMDRlZmNlNGNjNDcyMGI0ZDU2MGE5ZGQwOGNhMmQi.GNzvsfMsCITQ-xwfK-yl_TQwcLd4F-264wYK19frMXE'
    url = _url
    headers = {
        "Authorization": _authorization,
        "Content-Type": 'application/json'
    }
    response = requests.post(url, json=params, headers=headers)

    if response.status_code == 200:
        result = response.json()
        context = {
            'tipo_de_comprobante': result.get("tipo_de_comprobante"),
            'serie': result.get("serie"),
            'numero': result.get("numero"),
            'aceptada_por_sunat': result.get("aceptada_por_sunat"),
            'sunat_description': result.get("sunat_description"),
            'enlace_del_pdf': result.get("enlace_del_pdf"),
            'cadena_para_codigo_qr': result.get("cadena_para_codigo_qr"),
            'codigo_hash': result.get("codigo_hash"),
            'params': params
        }
    else:
        result = response.json()
        context = {
            'errors': result.get("errors"),
            'codigo': result.get("codigo"),
        }
    return context
