from django.shortcuts import render
from datetime import datetime
from http import HTTPStatus
from django.contrib.auth.models import User
from django.db.models import Min, Max, Sum, Count, Q
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
import decimal
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.template import loader
from datetime import datetime
from django.db import DatabaseError, IntegrityError
from django.core import serializers
from datetime import date

from apps.accounting.models import Casing, Payments
from apps.hrm.views import get_subsidiary_by_user
from apps.purchase.models import Provider
from apps.sale.models import Client, Product, ProductCategory, Unit, Coin, ProductPresenting, Kardex, ProductStore, \
    SubsidiaryStore, Order, OrderDetail, OrderBill
from apps.sale.views import get_order_correlative, minimum_unit, kardex_input
from apps.sale.views_SUNAT import query_dni, send_f_nubefact, send_b_nubefact
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder


def get_order_purchase(request):
    if request.method == 'GET':
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        # sales_store = SubsidiaryStore.objects.filter(
        #     subsidiary=subsidiary_obj, category='3').first()
        casing_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj).values('id',
                                                                                                             'name')
        provider_set = Provider.objects.all()
        # product_dic = []
        # if sales_store is None:
        #     error = "No existe almacen de ventas registrado, Favor de registre el almacen de ventas."
        # else:
        #
        #     for p in Product.objects.filter(is_state=True,
        #                                     productstore__subsidiary_store=sales_store,
        #                                     productpresenting__quantity_minimum=1).values('id',
        #                                                                                   'names', 'code', 'photo',
        #                                                                                   'stock_min', 'stock_max',
        #                                                                                   'productstore__stock',
        #                                                                                   'productpresenting__price_sale',
        #                                                                                   'productpresenting__unit__name'):
        #         new_product = {
        #             'id': p['id'],
        #             'name': p['names'],
        #             'code': p['code'],
        #             'photo': p['photo'],
        #             'path_cache': get_photo(p['photo']),
        #             'stock_min': p['stock_min'],
        #             'stock_max': p['stock_max'],
        #             'stock': p['productstore__stock'],
        #             'price': p['productpresenting__price_sale'],
        #             'unit': p['productpresenting__unit__name'],
        #         }
        #         product_dic.append(new_product)

        coin_set = Coin.objects.all().order_by('id')
        return render(request, 'purchase/order_purchase.html', {
            'date_now': date_now,
            # 'product_set': product_dic,
            'subsidiary_obj': subsidiary_obj,
            # 'sales_store': sales_store,
            'type_payment': Payments._meta.get_field('type_payment').choices,
            'casing_set': casing_set,
            'coin_set': coin_set,
            'bank_set': Payments._meta.get_field('type_bank').choices,
            'provider_set': provider_set,
        })


def get_details_purchase(request):
    if request.method == 'GET':
        product_set = Product.objects.all().values('id', 'names')
        t = loader.get_template('purchase/order_purchase_add.html')
        c = ({
            'product_set': product_set,
        })
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


def get_units_and_store_by_product(request):
    if request.method == 'GET':
        id_product = request.GET.get('ip', '')
        product_obj = Product.objects.get(pk=int(id_product))
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        stores = SubsidiaryStore.objects.filter(stores__product=product_obj, subsidiary=subsidiary_obj)
        stores_serialized_obj = serializers.serialize('json', stores)
        units = Unit.objects.filter(productpresenting__product=product_obj)
        units_serialized_obj = serializers.serialize('json', units)

        return JsonResponse({
            'units': units_serialized_obj,
            'stores': stores_serialized_obj,
        }, status=HTTPStatus.OK)


def create_order_purchase(request):
    if request.method == 'GET':
        dictionary_order_purchase = request.GET.get('order_purchase', '')
        data_order = json.loads(dictionary_order_purchase)
        provider_pk = int(data_order["provider"])
        provider_obj = Provider.objects.get(id=provider_pk)
        date_order = data_order["date_order"]
        invoice_order = data_order["invoice_order"]
        total_order = decimal.Decimal(data_order["purchase_total"])
        total_discount = decimal.Decimal(data_order["purchase_discount"])
        type_payment = str(data_order["type_payment"])
        user_id = request.user.id
        user_obj = User.objects.get(id=user_id)
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        new_order_purchase = {
            'type': 'C',
            'correlative_order': get_order_correlative(subsidiary_obj.id, 'C'),
            'status': 'C',
            'invoice': invoice_order,
            'create_at': date_order,
            'invoice': invoice_order,
            'provider': provider_obj,
            'total': total_order,
            'discount': total_discount,
            'user': user_obj,
            'subsidiary': subsidiary_obj,
        }
        order_purchase_obj = Order.objects.create(**new_order_purchase)
        order_purchase_obj.save()
        print(data_order['Details'])
        for detail in data_order['Details']:
            quantity = decimal.Decimal(detail['quantity'])
            price = decimal.Decimal(detail['price'])
            product_id = int(detail['product'])
            product_obj = Product.objects.get(id=product_id)
            unit_id = int(detail['unit'])
            unit_obj = Unit.objects.get(id=unit_id)
            new_detail_order = {
                'order': order_purchase_obj,
                'product': product_obj,
                'quantity': quantity,
                'price_unit': price,
                'unit': unit_obj,
            }
            new_detail_order_obj = OrderDetail.objects.create(**new_detail_order)
            new_detail_order_obj.save()

            try:
                quantity_minimum_unit = minimum_unit(quantity, unit_obj, product_obj)
                subsidiary_store_pk = int(detail['store'])
                subsidiary_store_obj = SubsidiaryStore.objects.get(id=subsidiary_store_pk)
                product_store_obj = ProductStore.objects.filter(subsidiary_store=subsidiary_store_obj,
                                                                product=product_obj).first()
            except ProductStore.DoesNotExist:
                product_store_obj = None

            if product_store_obj is None:
                new_product_store = {
                    'stock': quantity_minimum_unit,
                    'product': product_obj,
                    'subsidiary_store': subsidiary_store_obj
                }
                product_store_obj = ProductStore.objects.create(**new_product_store)
                product_store_obj.save()

            kardex_input(product_store_obj, quantity_minimum_unit, price,
                         order_detail_obj=new_detail_order_obj)
        if type_payment == 'E':
            amount_cash = decimal.Decimal(data_order["amount_cash"])
            cash_pk = int(data_order["cash"])
            cash_obj = Casing.objects.get(id=cash_pk)
            coin_pk = int(data_order["amount_coin"])
            coin_obj = Coin.objects.get(id=coin_pk)
            new_payment_e = {
                'order': order_purchase_obj,
                'type': 'E',
                'type_payment': type_payment,
                'amount': amount_cash,
                'coin': coin_obj,
                'date_payment': date_order,
                'user': user_obj,
                'subsidiary': subsidiary_obj,
                'casing': cash_obj,
            }
            new_payment_e_obj = Payments.objects.create(**new_payment_e)
            new_payment_e_obj.save()
        elif type_payment == 'D':
            deposit = str(data_order["deposit"])
            code_operation = str(data_order["code_operation"])
            amount_deposit = decimal.Decimal(data_order["amount_deposit"])
            new_payment_d = {
                'order': order_purchase_obj,
                'type': 'E',
                'type_payment': type_payment,
                'type_bank': deposit,
                'code_operation': code_operation,
                'amount': amount_deposit,
                'date_payment': date_order,
                'user': user_obj,
                'subsidiary': subsidiary_obj,
            }
            new_payment_d_obj = Payments.objects.create(**new_payment_d)
            new_payment_d_obj.save()
        return JsonResponse({
            'message': 'Compra registrada correctamente.',
        }, status=HTTPStatus.OK)


def get_provider_list(request):
    if request.method == 'GET':
        provider_set = Provider.objects.all()
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m")
        return render(request, 'purchase/provider_list.html', {
            'date_now': date_now,
            'provider_set': provider_set,
        })


def get_provider_form(request):
    if request.method == 'GET':
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        t = loader.get_template('purchase/provider_form.html')
        c = ({
            'date_now': date_now,
            'type_document': Provider._meta.get_field('type_document').choices,
        })
        return JsonResponse({
            'form': t.render(c, request),
        })


@csrf_exempt
def save_provider(request):
    if request.method == 'POST':
        _type_document = request.POST.get('document_type_sender', '')
        _document = request.POST.get('document', '')
        _full_names = request.POST.get('full_names', '').upper()
        _telephone_number = request.POST.get('telephone', '')
        _email = request.POST.get('email', '')
        _address = request.POST.get('address', '').upper()

        provider_obj = Provider(
            type_document=_type_document,
            document=_document,
            full_names=_full_names,
            telephone=_telephone_number,
            email=_email,
            address=_address
        )
        provider_obj.save()
        return JsonResponse({
            'success': True,
        }, status=HTTPStatus.OK)


def get_provider_update_form(request):
    if request.method == 'GET':
        pk = int(request.GET.get('pk', ''))
        provider_obj = Provider.objects.get(id=pk)
        t = loader.get_template('purchase/provider_update_form.html')
        c = ({
            'provider_obj': provider_obj,
            'type_document': Provider._meta.get_field('type_document').choices,
        })
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


@csrf_exempt
def update_provider(request):
    if request.method == 'POST':
        _id = int(request.POST.get('pk', ''))
        client_obj = Client.objects.get(id=_id)
        _type_document = request.POST.get('document_type_sender', '')
        _document = request.POST.get('document', '')
        _full_names = request.POST.get('full_names', '')
        _telephone_number = request.POST.get('telephone', '')
        _email = request.POST.get('email', '')
        _address = request.POST.get('address', '')

        client_obj.type_document = _type_document
        client_obj.document = _document
        client_obj.full_names = _full_names.upper()
        client_obj.telephone = _telephone_number
        client_obj.email = _email
        client_obj.address = _address.upper()
        client_obj.save()
        return JsonResponse({
            'success': True,
        }, status=HTTPStatus.OK)

