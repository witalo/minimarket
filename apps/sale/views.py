from datetime import datetime
from http import HTTPStatus
from django.contrib.auth.models import User
from django.db.models import Min, Max, Sum, Count, Q
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render
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
from apps.sale.models import Client, Product, ProductCategory, Unit, Coin, ProductPresenting, Kardex, ProductStore, \
    SubsidiaryStore, Order, OrderDetail, OrderBill
from apps.sale.views_SUNAT import query_dni, send_f_nubefact, send_b_nubefact, query_api_free_ruc, query_api_free_dni
from ventura import settings
import os


def calculate_age(birthdate):
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age


# Create your views here.
def get_photo(photo=None):
    # _path = str(settings.MEDIA_URL + p['photo']).replace('/', '\\')
    _path_real_cache = str(
        settings.MEDIA_ROOT + '/CACHE/images/' + photo.replace('.png', '/').replace('.jpg', '/')
    ).replace('/', '\\')
    dir_path = os.path.dirname(_path_real_cache)
    _file_name = ''
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.jpg'):
                _file_name = str(file)
    _path_cache = str(
        settings.MEDIA_URL + 'CACHE/images/' + photo.replace('.png', '/').replace('.jpg', '/') + _file_name
    )
    return _path_cache


def kardex_initial(
        product_store_obj,
        stock,
        price_unit,
        order_detail_obj=None,
):
    new_kardex = {
        'operation': 'C',
        'quantity': 0,
        'price_unit': 0,
        'price_total': 0,
        'remaining_quantity': decimal.Decimal(stock),
        'product_store': product_store_obj,
        'order_detail': order_detail_obj,
    }
    kardex_obj = Kardex.objects.create(**new_kardex)
    kardex_obj.save()


def kardex_input(
        product_store_obj,
        quantity,
        price_unit,
        order_detail_obj=None,
):
    old_stock = product_store_obj.stock
    new_quantity = decimal.Decimal(quantity)
    new_stock = old_stock + new_quantity
    new_price_unit = decimal.Decimal(price_unit)
    new_price_total = new_quantity * new_price_unit

    new_kardex = {
        'operation': 'E',
        'quantity': new_quantity,
        'price_unit': new_price_unit,
        'price_total': new_price_total,
        'remaining_quantity': new_stock,
        'product_store': product_store_obj,
        'order_detail': order_detail_obj,
    }
    kardex_obj = Kardex.objects.create(**new_kardex)
    kardex_obj.save()

    product_store_obj.stock = new_stock
    product_store_obj.save()


def kardex_output(
        product_store_obj,
        quantity,
        price_unit,
        order_detail_obj=None,
):
    old_stock = product_store_obj.stock
    if old_stock > decimal.Decimal(quantity):
        new_quantity = decimal.Decimal(quantity)
        new_stock = old_stock - new_quantity
        new_price_unit = decimal.Decimal(price_unit)
        new_price_total = new_quantity * new_price_unit

        new_kardex = {
            'operation': 'S',
            'quantity': new_quantity,
            'price_unit': new_price_unit,
            'price_total': new_price_total,
            'remaining_quantity': new_stock,
            'product_store': product_store_obj,
            'order_detail': order_detail_obj,
        }
        kardex_obj = Kardex.objects.create(**new_kardex)
        kardex_obj.save()

        product_store_obj.stock = new_stock
        product_store_obj.save()


def kardex_readjusting(
        product_store_obj,
        quantity,
        order_detail_obj=None,
):
    kardex_obj = Kardex.objects.filter(product_store=product_store_obj).last()
    last_remaining_quantity = kardex_obj.remaining_quantity
    new_quantity = abs(last_remaining_quantity - decimal.Decimal(quantity))

    new_kardex = {
        'operation': 'R',
        'quantity': new_quantity,
        'price_unit': 0,
        'price_total': 0,
        'remaining_quantity': decimal.Decimal(quantity),
        'product_store': product_store_obj,
        'order_detail': order_detail_obj,
    }
    kardex_obj = Kardex.objects.create(**new_kardex)
    kardex_obj.save()

    product_store_obj.stock = decimal.Decimal(quantity)
    product_store_obj.save()


def minimum_unit(quantity, unit_obj, product_obj):
    try:
        # quantity_min = ProductPresenting.objects.filter(
        #     product=product_obj).aggregate(Min('quantity_minimum'))
        quantity_presenting = ProductPresenting.objects.filter(product_id=product_obj.id, unit=unit_obj).aggregate(
            Min('quantity_minimum'))
    except ProductPresenting.DoesNotExist:
        return 0
    new_quantity = quantity_presenting['quantity_minimum__min'] * decimal.Decimal(quantity)
    # if decimal.Decimal(quantity_min['quantity_minimum__min']) > 1:
    #     new_quantity = quantity * decimal.Decimal(quantity_min['quantity_minimum__min'])
    # else:
    #     new_quantity = quantity * decimal.Decimal(
    #         quantity_min['quantity_minimum__min']) * product_detail_sent.quantity_minimum
    return new_quantity


def get_client_list(request):
    if request.method == 'GET':
        client_set = Client.objects.all()
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m")
        return render(request, 'sale/client_list.html', {
            'date_now': date_now,
            'client_set': client_set,
        })


def get_client_form(request):
    if request.method == 'GET':
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        t = loader.get_template('sale/client_form.html')
        c = ({
            'date_now': date_now,
            'type_document': Client._meta.get_field('type_document').choices,
        })
        return JsonResponse({
            'form': t.render(c, request),
        })


@csrf_exempt
def save_client(request):
    if request.method == 'POST':
        _type_document = request.POST.get('document_type_sender', '')
        _document = request.POST.get('document', '')
        _full_names = request.POST.get('full_names', '').upper()
        _telephone_number = request.POST.get('telephone', '')
        _email = request.POST.get('email', '')
        _address = request.POST.get('address', '').upper()

        client_obj = Client(
            type_document=_type_document,
            document=_document,
            full_names=_full_names,
            telephone_number=_telephone_number,
            email=_email,
            address=_address
        )
        client_obj.save()
        return JsonResponse({
            'success': True,
        }, status=HTTPStatus.OK)


def get_client_update_form(request):
    if request.method == 'GET':
        pk = int(request.GET.get('pk', ''))
        client_obj = Client.objects.get(id=pk)
        t = loader.get_template('sale/client_update_form.html')
        c = ({
            'client_obj': client_obj,
            'type_document': Client._meta.get_field('type_document').choices,
        })
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


@csrf_exempt
def update_client(request):
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
        client_obj.document_number = _document
        client_obj.full_names = _full_names.upper()
        client_obj.telephone_number = _telephone_number
        client_obj.email = _email
        client_obj.address = _address.upper()
        client_obj.save()
        return JsonResponse({
            'success': True,
        }, status=HTTPStatus.OK)


def get_product_view(request):
    if request.method == 'GET':
        product_set = Product.objects.all()
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m")
        product_dic = []
        for p in Product.objects.filter(is_state=True).values('id',
                                                              'names', 'code', 'photo',
                                                              'stock_min', 'stock_max', ):
            new_product = {
                'id': p['id'],
                'name': p['names'],
                'code': p['code'],
                'photo': p['photo'],
                'path_cache': get_photo(p['photo']),
                'stock_min': p['stock_min'],
                'stock_max': p['stock_max'],
            }
            product_dic.append(new_product)

        return render(request, 'sale/product_list.html', {
            'date_now': date_now,
            'product_set': product_dic,
        })


def get_product_form(request):
    if request.method == 'GET':
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        category_set = ProductCategory.objects.all()
        t = loader.get_template('sale/product_form.html')
        c = ({
            'date_now': date_now,
            'category_set': category_set,
            'type': Product._meta.get_field('type').choices,
        })
        return JsonResponse({
            'form': t.render(c, request),
        })


@csrf_exempt
def save_product(request):
    if request.method == 'POST':
        _code = request.POST.get('code', '').upper()
        _names = request.POST.get('name', '').upper()
        _stock_min = request.POST.get('minimum', '')
        _stock_max = request.POST.get('maximum', '')
        _product_category = request.POST.get('category', '')
        category_obj = ProductCategory.objects.get(id=int(_product_category))
        _type = request.POST.get('type', '')
        try:
            _photo = request.FILES['route']
        except Exception as e:
            _photo = 'product/product0.jpg'
        _state = bool(request.POST.get('state', ''))

        product_obj = Product(
            code=_code,
            names=_names,
            stock_min=_stock_min,
            stock_max=_stock_max,
            product_category=category_obj,
            type=_type,
            is_state=_state,
            photo=_photo,
        )
        product_obj.save()
        return JsonResponse({
            'success': True,
            'message': 'Registro guardado',
        }, status=HTTPStatus.OK)


def get_product_update_form(request):
    if request.method == 'GET':
        product_id = int(request.GET.get('pk_', ''))
        product_obj = Product.objects.get(id=product_id)
        category_set = ProductCategory.objects.all()
        t = loader.get_template('sale/product_update_form.html')
        c = ({
            'product_obj': product_obj,
            'category_set': category_set,
            'type': Product._meta.get_field('type').choices,
        })
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


@csrf_exempt
def update_product(request):
    if request.method == 'POST':

        _id = int(request.POST.get('pk', ''))
        product_obj = Product.objects.get(id=_id)
        _names = request.POST.get('name', '').upper()
        _photo = request.FILES.get('route', False)
        _code = request.POST.get('code', '').upper()
        _category_id = int(request.POST.get('category', ''))
        category_obj = ProductCategory.objects.get(id=_category_id)
        _type = request.POST.get('type', '')
        _state = bool(request.POST.get('state', ''))
        _stock_min = request.POST.get('minimum', '')
        _stock_max = request.POST.get('maximum', '')

        product_obj.code = _code
        product_obj.names = _names
        product_obj.stock_min = _stock_min
        product_obj.stock_max = _stock_max
        product_obj.product_category = category_obj
        product_obj.type = _type
        product_obj.is_state = _state
        if _photo is not False:
            product_obj.photo = _photo
        product_obj.save()
        return JsonResponse({
            'success': True,
        }, status=HTTPStatus.OK)


def product_presenting_operation(request):
    data = {}
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        try:
            product_obj = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            data['error'] = "El producto no existe!"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        products = Product.objects.all()
        units = Unit.objects.all()
        coins = Coin.objects.all()
        t = loader.get_template('sale/product_presenting.html')
        c = ({
            'product': product_obj,
            'units': units,
            'products': products,
            'coins': coins,
        })

        product_presenting = ProductPresenting.objects.filter(product=product_obj).order_by('id')
        tpl2 = loader.get_template('sale/product_presenting_detail.html')
        context2 = ({'product_presenting': product_presenting, })
        serialized_data = serializers.serialize('json', product_presenting)
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
            'grid': tpl2.render(context2),
            'serialized_data': serialized_data,
            # 'form': t.render(c),
        }, status=HTTPStatus.OK)
    else:
        if request.method == 'POST':
            _product_id = request.POST.get('product', '')
            _price_sale = request.POST.get('price_sale', '')
            _id_unit = request.POST.get('unit', '')
            _quantity_minimum = request.POST.get('quantity_minimum', '')
            _coin = request.POST.get('coin_sale', '')

            if decimal.Decimal(_price_sale) == 0 or decimal.Decimal(_quantity_minimum) == 0:
                data['error'] = "Ingrese valores validos."
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response

            product_obj = Product.objects.get(id=int(_product_id))
            unit_obj = Unit.objects.get(id=int(_id_unit))
            coin_obj = Coin.objects.get(id=int(_coin))

            try:
                product_presenting_obj = ProductPresenting(
                    product=product_obj,
                    price_sale=decimal.Decimal(_price_sale),
                    unit=unit_obj,
                    quantity_minimum=decimal.Decimal(_quantity_minimum),
                    coin=coin_obj,
                )
                product_presenting_obj.save()
            except DatabaseError as e:
                data['error'] = 'Verifique que la unidad de medida sea distinta'  # str(e)
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response
            except IntegrityError as e:
                data['error'] = str(e)
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response

            _product_presenting = ProductPresenting.objects.filter(product=product_obj).order_by('id')
            tpl2 = loader.get_template('sale/product_presenting_detail.html')
            context2 = ({'product_presenting': _product_presenting, })

            return JsonResponse({
                'message': 'Registro ingresado correctamente.',
                'grid': tpl2.render(context2),
            }, status=HTTPStatus.OK)


def update_product_presenting(request):
    data = dict()
    if request.method == 'POST':
        _presenting_id = request.POST.get('product_presenting', '')
        _product_id = request.POST.get('product', '')
        _price_sale = request.POST.get('price_sale', '')
        _unit_id = request.POST.get('unit', '')
        _quantity_minimum = request.POST.get('quantity_minimum', '')
        _coin = request.POST.get('coin_sale', '')

        if decimal.Decimal(_price_sale) == 0 or decimal.Decimal(_quantity_minimum) == 0:
            data['error'] = "Ingrese valores validos."
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        product_obj = Product.objects.get(id=int(_product_id))
        unit_obj = Unit.objects.get(id=int(_unit_id))
        coin_obj = Coin.objects.get(id=int(_coin))

        product_detail_obj = ProductPresenting.objects.get(id=int(_presenting_id))
        product_detail_obj.quantity_minimum = decimal.Decimal(_quantity_minimum)
        product_detail_obj.price_sale = decimal.Decimal(_price_sale)
        product_detail_obj.product = product_obj
        product_detail_obj.unit = unit_obj
        product_detail_obj.coin = coin_obj
        product_detail_obj.save()

        product_presenting = ProductPresenting.objects.filter(product=product_obj).order_by('id')
        tpl2 = loader.get_template('sale/product_presenting_detail.html')
        context2 = ({'product_presenting': product_presenting, })

        return JsonResponse({
            'message': 'Registro actualizado correctamente.',
            'grid': tpl2.render(context2),
        }, status=HTTPStatus.OK)
    return JsonResponse({'message': 'Problemas con la conección.'}, status=HTTPStatus.BAD_REQUEST)


def get_product_presenting(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        product_presenting_obj = ProductPresenting.objects.filter(id=pk)
        serialized_obj = serializers.serialize('json', product_presenting_obj)
        return JsonResponse({'_object': serialized_obj}, status=HTTPStatus.OK)
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


def status_product_presenting(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        text_status = request.GET.get('status', '')
        status = False
        if text_status == 'True':
            status = True
        product_presenting_obj = ProductPresenting.objects.get(id=pk)
        product_presenting_obj.is_enabled = status
        product_presenting_obj.save()
        return JsonResponse({'message': 'Proceso con exito.'}, status=HTTPStatus.OK)
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


def delete_product_presenting(request):
    if request.method == 'GET':
        product_presenting_id = int(request.GET.get('pk', ''))
        product_presenting_obj = ProductPresenting.objects.get(id=product_presenting_id)
        product_presenting_obj.delete()
        return JsonResponse({
            'success': True,
        })


def get_template_initial(request):
    data = {}
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        try:
            product_obj = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            data['error'] = "El producto no esta registrado!"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        subsidiary_store_set = SubsidiaryStore.objects.filter(subsidiary=subsidiary_obj)
        units = Unit.objects.filter(productpresenting__product=product_obj)

        t = loader.get_template('sale/product_initial_store.html')
        c = ({'product': product_obj,
              'subsidiary': subsidiary_obj,
              'subsidiary_store_set': subsidiary_store_set,
              'units': units,
              })
        product_store_set = ProductStore.objects.filter(product=product_obj,
                                                        subsidiary_store__subsidiary=subsidiary_obj)
        product_presenting = ProductPresenting.objects.filter(
            product=product_obj).annotate(Min('quantity_minimum'))
        unit_min_obj = None
        if product_presenting.count() > 0:
            unit_min_obj = product_presenting.first().unit
        tpl2 = loader.get_template('sale/product_initial_store_detail.html')
        context2 = ({'product_store_set': product_store_set, 'unit_min': unit_min_obj, 'units': units, })
        serialized_data = serializers.serialize('json', product_presenting)
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
            'grid': tpl2.render(context2),
            'serialized_data': serialized_data,
        }, status=HTTPStatus.OK)
    else:
        if request.method == 'POST':
            if request.POST.get('subsidiary-store', '') == '0':
                data['error'] = "Seleccione el almacen de la sede"
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response
            if request.POST.get('unit-store', '') == '0':
                data['error'] = "Seleccione la unidad de medida"
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response
            _subsidiary_store_id = request.POST.get('subsidiary-store', '')
            _quantity = request.POST.get('quantity-store', '')
            _id_unit = request.POST.get('unit-store', '')
            _id_product = request.POST.get('product', '')
            product_obj = Product.objects.get(id=int(_id_product))
            unit_obj = Unit.objects.get(id=int(_id_unit))
            new_quantity = minimum_unit(_quantity, unit_obj, product_obj)
            subsidiary_store_obj = SubsidiaryStore.objects.get(id=int(_subsidiary_store_id))
            if decimal.Decimal(_quantity) == 0:
                data['error'] = "Ingrese un numero decimal en la cantidad."
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response
            try:
                new_product_store = {
                    'stock': decimal.Decimal(new_quantity),
                    'product': product_obj,
                    'subsidiary_store': subsidiary_store_obj,
                }
                product_store_obj = ProductStore.objects.create(**new_product_store)
                product_store_obj.save()
                kardex_initial(product_store_obj, decimal.Decimal(new_quantity), 0)
            except DatabaseError as e:
                data['error'] = str(e)
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response
            except IntegrityError as e:
                data['error'] = str(e)
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response
            user_id = request.user.id
            user_obj = User.objects.get(id=int(user_id))
            subsidiary_obj = get_subsidiary_by_user(user_obj)
            units = Unit.objects.filter(productpresenting__product=product_obj)
            product_store_set = ProductStore.objects.filter(product=product_obj,
                                                            subsidiary_store__subsidiary=subsidiary_obj)
            product_presenting = ProductPresenting.objects.filter(
                product=product_obj).annotate(Min('quantity_minimum'))
            unit_min_obj = None
            if product_presenting.count() > 0:
                unit_min_obj = product_presenting.first().unit
            tpl2 = loader.get_template('sale/product_initial_store_detail.html')
            context2 = ({'product_store_set': product_store_set, 'unit_min': unit_min_obj, 'units': units, })

            return JsonResponse({
                'message': 'Stock creado correctamente.',
                'grid': tpl2.render(context2),
            }, status=HTTPStatus.OK)


def update_product_store_by_subsidiary_store(request):
    data = {}
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        if pk == '':
            data['error'] = "No se logro obtener el almacen del producto"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        product_store_obj = ProductStore.objects.get(id=int(pk))
        stock = request.GET.get('stock', '')
        if stock == '' or stock < 0:
            data['error'] = "La cantidad debe ser un valor mayor que cero"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        unit = request.GET.get('unit', '0')
        if unit == '0':
            data['error'] = "Seleccione la unidad de medida"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        unit_obj = Unit.objects.get(id=int(unit))
        product = request.GET.get('product', '')
        if product == '':
            data['error'] = "No se a obtenido correctamente el producto"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        product_obj = Product.objects.get(id=int(product))
        new_quantity = minimum_unit(decimal.Decimal(stock), unit_obj, product_obj)
        kardex_readjusting(product_store_obj, new_quantity)
        return JsonResponse({
            'success': True,
            'message': 'Stock actualizado correctamente.',
        }, status=HTTPStatus.OK)


def get_kardex_by_product(request):
    data = dict()
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        try:
            product = Product.objects.get(id=int(pk))
        except Product.DoesNotExist:
            data['error'] = "producto no existe!"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        products = Product.objects.all()
        subsidiaries_stores = SubsidiaryStore.objects.all()
        basic_product_detail = ProductPresenting.objects.filter(
            product=product, quantity_minimum=1)
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m")
        t = loader.get_template('sale/kardex.html')
        c = ({
            'product': product,
            'date_now': date_now,
            'basic_product_detail': basic_product_detail,
            'subsidiaries_stores': subsidiaries_stores,
            'products': products,
        })

        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


def get_list_kardex(request):
    data = dict()
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        _mount = request.GET.get('mount', '')
        pk_subsidiary_store = request.GET.get('subsidiary_store', '')
        if _mount == '':
            data['error'] = "Seleccione el mes"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        try:
            product_obj = Product.objects.get(id=int(pk))
        except Product.DoesNotExist:
            data['error'] = "Producto no se a identificado!"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        if pk_subsidiary_store == '' or pk_subsidiary_store == '0':
            data['error'] = "Seleccione un almacen de la sede"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        subsidiary_store_obj = SubsidiaryStore.objects.get(id=int(pk_subsidiary_store))
        try:
            product_store_set = ProductStore.objects.filter(
                product=product_obj).filter(subsidiary_store=subsidiary_store_obj)

        except ProductStore.DoesNotExist:
            data['error'] = "almacen producto no existe!"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        date_time_obj = datetime.strptime(_mount, '%Y-%m')
        new_year = date_time_obj.year
        new_month = date_time_obj.month
        inventories = None
        if product_store_set.count() > 0:
            inventories = Kardex.objects.filter(product_store=product_store_set[0], create_at__year=new_year,
                                                create_at__month=new_month).order_by('id')

        t = loader.get_template('sale/kardex_grid_list.html')
        c = ({'product': product_obj, 'inventories': inventories})

        return JsonResponse({
            'success': True,
            'form': t.render(c),
        })


def get_order_sales(request):
    if request.method == 'GET':
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        sales_store = SubsidiaryStore.objects.filter(
            subsidiary=subsidiary_obj, category='3').first()
        product_set = Product.objects.filter(is_state=True, productstore__subsidiary_store=sales_store)
        casing_set = Casing.objects.filter(user=user_obj, is_enabled=True, subsidiary=subsidiary_obj).values('id',
                                                                                                             'name')
        coin_set = Coin.objects.all().order_by('id')
        return render(request, 'sale/order_sales.html', {
            'date_now': date_now,
            'product_set': product_set,
            'subsidiary_obj': subsidiary_obj,
            'sales_store': sales_store,
            'type_document': Client._meta.get_field('type_document').choices,
            'type_payment': Payments._meta.get_field('type_payment').choices,
            'casing_set': casing_set,
            'coin_set': coin_set,
            'bank_set': Payments._meta.get_field('type_bank').choices,
        })


def get_client_by_document(request):
    if request.method == 'GET':
        number_document = request.GET.get('number_document', '')
        type_document = request.GET.get('type_document', '')
        try:
            client_obj_search = Client.objects.get(document=number_document)
        except Client.DoesNotExist:
            client_obj_search = None
        if client_obj_search is not None:
            return JsonResponse({
                'pk': client_obj_search.id,
                'names': client_obj_search.full_names,
                'address': client_obj_search.address},
                status=HTTPStatus.OK)

        else:
            if type_document == '01':
                type_name = 'DNI'
                r = query_api_free_dni(number_document, type_name)
                if r.get('status') is True:
                    name = r.get('Nombre')
                    paternal_name = r.get('Paterno')
                    maternal_name = r.get('Materno')
                    # get_birthday = r.get('FechaNac')
                    if paternal_name is not None and len(paternal_name) > 0:
                        result = name + ' ' + paternal_name + ' ' + maternal_name
                        if len(result.strip()) != 0:
                            client_obj = Client(
                                type_document=type_document,
                                document=number_document,
                                full_names=result,
                            )
                            client_obj.save()

                        else:
                            data = {'error': 'No existe el DNI, Registre manualmente'}
                            response = JsonResponse(data)
                            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                            return response
                else:
                    data = {
                        'error': 'No se encontro el dni en la reniec, Registre manualmentE'}
                    response = JsonResponse(data)
                    response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                    return response

            elif type_document == '06':
                type_name = 'RUC'
                r = query_api_free_ruc(number_document, type_name)
                if r.get('ruc') == number_document:
                    name_business = r.get('razonSocial')
                    address_business = r.get('direccion')

                    client_obj = Client(
                        type_document=type_document,
                        document=number_document,
                        full_names=name_business,
                        address=address_business,
                    )
                    client_obj.save()
                else:
                    data = {'error': 'No se encontro el RUC, Registre manualmente'}
                    response = JsonResponse(data)
                    response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                    return response

        return JsonResponse({
            'pk': client_obj.id,
            'names': client_obj.full_names,
            'address': client_obj.address},
            status=HTTPStatus.OK)
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


def get_prices_by_product(request):
    if request.method == 'GET':
        id_product = request.GET.get('pk', '')
        product_obj = Product.objects.get(id=int(id_product))
        product_presenting_set = ProductPresenting.objects.filter(product=product_obj)
        user_id = request.user.id
        user_obj = User.objects.get(pk=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        product_stores_obj = ProductStore.objects.filter(product=product_obj,
                                                         subsidiary_store__subsidiary=subsidiary_obj,
                                                         subsidiary_store__category='3').first()
        tpl = loader.get_template('sale/order_sale_rate.html')
        context = ({
            'product_store': product_stores_obj,
            'product_presenting_set': product_presenting_set,
        })

        return JsonResponse({
            'grid': tpl.render(context),
        }, status=HTTPStatus.OK)


def get_order_correlative(pk, o_type):
    value_max = 1
    order_set = Order.objects.filter(subsidiary_id=pk, type=o_type).aggregate(Max('correlative_order'))
    if order_set['correlative_order__max']:
        value_max = value_max + order_set['correlative_order__max']
        return value_max
    else:
        return value_max


def create_order_sales(request):
    if request.method == 'GET':
        dictionary_order_sales = request.GET.get('order_sales', '')
        data_order = json.loads(dictionary_order_sales)
        client_pk = int(data_order["client"])
        client_obj = Client.objects.get(id=client_pk)
        serial_order = str(data_order["serial_order"])
        date_order = data_order["date_order"]
        total_order = decimal.Decimal(data_order["sale_total"])
        total_discount = decimal.Decimal(data_order["sale_discount"])
        voucher_order = str(data_order["type_voucher"])
        type_payment = str(data_order["type_payment"])
        user_id = request.user.id
        user_obj = User.objects.get(id=user_id)
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        new_order_sale = {
            'type': 'V',
            'correlative_order': get_order_correlative(subsidiary_obj.id, 'V'),
            'status': 'C',
            'create_at': date_order,
            'client': client_obj,
            'total': total_order,
            'discount': total_discount,
            'user': user_obj,
            'subsidiary': subsidiary_obj,
        }
        order_sale_obj = Order.objects.create(**new_order_sale)
        order_sale_obj.save()
        for detail in data_order['Details']:
            quantity = decimal.Decimal(detail['quantity'])
            price = decimal.Decimal(detail['price'])
            product_id = int(detail['product'])
            product_obj = Product.objects.get(id=product_id)
            unit_id = int(detail['unit'])
            unit_obj = Unit.objects.get(id=unit_id)
            new_detail_order = {
                'order': order_sale_obj,
                'product': product_obj,
                'quantity': quantity,
                'price_unit': price,
                'unit': unit_obj,
            }
            new_detail_order_obj = OrderDetail.objects.create(**new_detail_order)
            new_detail_order_obj.save()

            try:
                quantity_minimum_unit = minimum_unit(quantity, unit_obj, product_obj)
                product_store_pk = int(detail['store_pk'])
                product_store_obj = ProductStore.objects.get(id=product_store_pk)
            except ProductStore.DoesNotExist:
                product_store_obj = None

            kardex_output(product_store_obj, quantity_minimum_unit, price,
                          order_detail_obj=new_detail_order_obj)
        if type_payment == 'E':
            amount_cash = decimal.Decimal(data_order["amount_cash"])
            cash_pk = int(data_order["cash"])
            cash_obj = Casing.objects.get(id=cash_pk)
            coin_pk = int(data_order["amount_coin"])
            coin_obj = Coin.objects.get(id=coin_pk)
            new_payment_e = {
                'order': order_sale_obj,
                'type': 'I',
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
                'order': order_sale_obj,
                'type': 'I',
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

        if voucher_order != 'I':
            r = ''
            if voucher_order == 'F' & str(serial_order) != '':
                r = send_f_nubefact(order_sale_obj.id, str(voucher_order) + str(serial_order))
            elif voucher_order == 'B' & str(serial_order) != '':
                r = send_b_nubefact(order_sale_obj.id, str(voucher_order) + str(serial_order))
            if r != '':
                message_s = r.get('sunat_description')
                link_pdf = r.get('enlace_del_pdf')
                code_hash = r.get('codigo_hash')
                if code_hash:
                    order_bill_obj = OrderBill(order=order_sale_obj,
                                               type=r.get('tipo_de_comprobante'),
                                               serial=r.get('serie'),
                                               sunat_status=r.get('aceptada_por_sunat'),
                                               sunat_description=r.get('sunat_description'),
                                               user=user_obj,
                                               sunat_enlace_pdf=r.get('enlace_del_pdf'),
                                               code_qr=r.get('cadena_para_codigo_qr'),
                                               code_hash=r.get('codigo_hash'),
                                               number_receipt=r.get('numero'),
                                               status='E',
                                               created_at=date_order,
                                               )
                    order_bill_obj.save()
                else:
                    if r.get('errors'):
                        data = {'error': str(r.get('errors'))}
                    elif r.get('error'):
                        data = {'error': str(r.get('error'))}
                    response = JsonResponse(data)
                    response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                    return response
                return JsonResponse({
                    'message': 'Comprobante realizado con exito.',
                    'message_s': message_s,
                    'link': link_pdf,
                }, status=HTTPStatus.OK)
            else:
                data = {'error': 'La venta se registro, perono nose logro generar el comprobante'}
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response
        else:
            return JsonResponse({
                'message': 'Venta registrada correctamente.',
                '_pk': order_sale_obj.id,
            }, status=HTTPStatus.OK)
