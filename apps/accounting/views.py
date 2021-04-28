from datetime import datetime
from http import HTTPStatus
from django.contrib.auth.models import User
from django.db.models import Min, Max, Sum, Count, Q
from django.db.models.functions import Coalesce
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
from apps.hrm.models import Employee
from apps.hrm.views import get_subsidiary_by_user
from apps.sale.models import Client, Product, ProductCategory, Unit, Coin, ProductPresenting, Kardex, ProductStore, \
    SubsidiaryStore, Order


def get_valid_opening_cash(request):
    if request.method == 'GET':
        id_cash = request.GET.get('cash-id', '')
        casing_obj = Casing.objects.get(id=int(id_cash))
        user_id = request.user.id
        user_obj = User.objects.get(pk=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        try:
            payment_opening_obj = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj,
                                                          type_payment='E', type='A').last()
        except Payments.DoesNotExist:
            payment_opening_obj = None

        try:
            payment_closing_obj = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj,
                                                          type_payment='E', type='C').last()
        except Payments.DoesNotExist:
            payment_closing_obj = None

        if payment_opening_obj is not None:
            if payment_closing_obj is not None:
                if payment_closing_obj.id <= payment_opening_obj.id:
                    return JsonResponse({
                        'success': True,
                        'pk': 1,
                    }, status=HTTPStatus.OK)
                else:
                    return JsonResponse({
                        'success': True,
                        'pk': 0,
                    }, status=HTTPStatus.OK)
            else:
                return JsonResponse({
                    'success': True,
                    'pk': 1,
                }, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                'success': True,
                'pk': 0,
            }, status=HTTPStatus.OK)


# ------------------modal para la apertura-------------------
def get_opening_casing(request):
    if request.method == 'GET':
        operation = request.GET.get('operation', '')
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%dT%H:%M")
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        casing_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj).values('id',
                                                                                              'name')
        coin_set = Coin.objects.filter(is_enabled=True).values('id', 'name_coin')
        tpl = loader.get_template('accounting/opening_casing.html')
        context = ({
            'date_now': date_now,
            'casing_set': casing_set,
            'coin_set': coin_set,
        })

        return JsonResponse({
            'grid': tpl.render(context),
        }, status=HTTPStatus.OK, content_type="application/json")


# ----------validar caja si esta disponible para aperturarla------------
def get_validate_aperture(request):
    if request.method == 'GET':
        pk = request.GET.get('pk_cash', '')
        casing_obj = Casing.objects.get(id=int(pk))
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        try:
            payment_opening_obj = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj,
                                                          type_payment='E', type='A').last()
        except Payments.DoesNotExist:
            payment_opening_obj = None

        try:
            payment_closing_obj = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj,
                                                          type_payment='E', type='C').last()
        except Payments.DoesNotExist:
            payment_closing_obj = None

        if payment_opening_obj is not None:
            if payment_closing_obj is not None:
                if payment_closing_obj.id <= payment_opening_obj.id:
                    return JsonResponse({
                        'success': False,
                        'message': 'La caja ya se encuentra aperturada',
                    }, status=HTTPStatus.OK)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'La caja ya se encuentra aperturada',
                }, status=HTTPStatus.OK)

    return JsonResponse({
        'success': True,
    }, status=HTTPStatus.OK)


# ---------------Aperturar caja-------------------
@csrf_exempt
def opening_casing_a(request):
    if request.method == 'POST':
        _date = request.POST.get('date-aperture', '')
        _cashing_pk = request.POST.get('opening-cash', '')
        casing_obj = Casing.objects.get(id=int(_cashing_pk))
        _amount = decimal.Decimal(request.POST.get('amount-opening-cash', ''))
        _coin = request.POST.get('coin-opening-cash', '')
        coin_obj = Coin.objects.get(id=int(_coin))
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)

        payment_obj = Payments(
            type='A',
            type_payment='E',
            amount=_amount,
            coin=coin_obj,
            date_payment=_date,
            user=user_obj,
            subsidiary=subsidiary_obj,
            casing=casing_obj,
        )
        payment_obj.save()
        return JsonResponse({
            'success': True,
            'message': 'Caja aperturada con exito',
        }, status=HTTPStatus.OK)


# ----------modal cierre de caja------------------------
def get_closing_casing(request):
    if request.method == 'GET':
        dates = datetime.now()
        date_now = dates.strftime("%Y-%m-%dT%H:%M")
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        casing_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj).values('id',
                                                                                              'name')
        tpl = loader.get_template('accounting/closing_casing.html')
        context = ({
            'date_now': date_now,
            'casing_set': casing_set,
        })

        return JsonResponse({
            'grid': tpl.render(context),
        }, status=HTTPStatus.OK, content_type="application/json")


@csrf_exempt
def closing_casing_c(request):
    if request.method == 'POST':
        _date = request.POST.get('date-closing', '')
        _cashing_pk = request.POST.get('closing-cash', '')
        _amount_aperture = (request.POST.get('amount-aperture-casing', ''))
        _amount_cash = (request.POST.get('amount-cash-casing', ''))
        if _amount_aperture == '':
            _amount_aperture = 0
        if _amount_cash == '':
            _amount_cash = 0
        _total_cash = decimal.Decimal(_amount_cash) + decimal.Decimal(_amount_aperture)
        casing_obj = Casing.objects.get(id=int(_cashing_pk))
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        coin_obj = Coin.objects.get(abbreviation='S/.')
        payment_obj = Payments(
            type='C',
            type_payment='E',
            amount=decimal.Decimal(_total_cash),
            coin=coin_obj,
            date_payment=_date,
            user=user_obj,
            subsidiary=subsidiary_obj,
            casing=casing_obj,
        )
        payment_obj.save()
        return JsonResponse({
            'success': True,
            'pk': payment_obj.id,
            'message': 'Caja cerrada exitosamente',
        }, status=HTTPStatus.OK)


def get_total_casing(request):
    data = {}
    if request.method == 'GET':
        pk = request.GET.get('pk_cash', '')
        casing_obj = Casing.objects.get(id=int(pk))
        date_closing = request.GET.get('date_closing', '')
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        try:
            payment_aperture_obj = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj,
                                                           type_payment='E', type='A').last()
        except Payments.DoesNotExist:
            data['error'] = "La caja no se encuentra aperturada, imposible cerrar la caja"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response

        try:
            payment_closing_obj = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj,
                                                          type_payment='E', type='C').last()
        except Payments.DoesNotExist:
            payment_closing_obj = None
        if payment_aperture_obj is not None:
            if payment_closing_obj is not None:
                if payment_closing_obj.id < payment_aperture_obj.id:
                    return JsonResponse({
                        'success': True,
                        'result': get_total(casing_obj, subsidiary_obj, payment_aperture_obj),
                    }, status=HTTPStatus.OK, content_type="application/json")
                else:
                    data['error'] = "La caja no se encuentra aperturada, imposible cerrar la caja"
                    response = JsonResponse(data)
                    response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                    return response
            else:
                return JsonResponse({
                    'success': True,
                    'result': get_total(casing_obj, subsidiary_obj, payment_aperture_obj),
                }, status=HTTPStatus.OK, content_type="application/json")
        else:
            data['error'] = "La caja no se encuentra aperturada, imposible cerrar la caja"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response


def get_total(casing_obj=None, subsidiary_obj=None, payment_aperture_obj=None):
    total = []
    if payment_aperture_obj is not None:
        total_aperture = decimal.Decimal(0.00)
        total_cash_sales = decimal.Decimal(0.00)
        total_cash_purchase = decimal.Decimal(0.00)
        total_deposit_sales = decimal.Decimal(0.00)
        total_deposit_purchase = decimal.Decimal(0.00)
        total_credit_sales = decimal.Decimal(0.00)
        total_credit_purchase = decimal.Decimal(0.00)
        total_aperture = payment_aperture_obj.amount
        payment_set = Payments.objects.filter(subsidiary=subsidiary_obj,
                                              create_at__gte=payment_aperture_obj.create_at)
        payment_total_cash_sales = payment_set.filter(casing=casing_obj, type_payment='E', type='I').aggregate(
            r=Coalesce(Sum('amount'), 0))
        if payment_total_cash_sales is not None:
            total_cash_sales = payment_total_cash_sales['r']
        payment_total_cash_purchase = payment_set.filter(casing=casing_obj, type_payment='E', type='E').aggregate(
            r=Coalesce(Sum('amount'), 0))
        if payment_total_cash_purchase is not None:
            total_cash_purchase = payment_total_cash_purchase['r']

        payment_total_deposit_sales = payment_set.filter(type_payment='D', type='I').aggregate(
            r=Coalesce(Sum('amount'), 0))
        if payment_total_deposit_sales is not None:
            total_deposit_sales = payment_total_deposit_sales['r']

        payment_total_deposit_purchase = payment_set.filter(type_payment='D', type='E').aggregate(
            r=Coalesce(Sum('amount'), 0))
        if payment_total_deposit_purchase is not None:
            total_deposit_purchase = payment_total_deposit_purchase['r']

        payment_total_credit_sales = payment_set.filter(type_payment='C', type='I').aggregate(
            r=Coalesce(Sum('amount'), 0))
        if payment_total_credit_sales is not None:
            total_credit_sales = payment_total_credit_sales['r']

        payment_total_credit_purchase = payment_set.filter(type_payment='C', type='E').aggregate(
            r=Coalesce(Sum('amount'), 0))
        if payment_total_credit_purchase is not None:
            total_credit_purchase = payment_total_credit_purchase['r']
        new_total = {
            'total_aperture': round(total_aperture, 2),
            'total_cash_sales': round(total_cash_sales, 2),
            'total_cash_purchase': round(total_cash_purchase, 2),
            'total_deposit_sales': round(total_deposit_sales, 2),
            'total_deposit_purchase': round(total_deposit_purchase, 2),
            'total_credit_sales': round(total_credit_sales, 2),
            'total_credit_purchase': round(total_credit_purchase, 2),
            'total_cash': round(total_cash_sales - total_cash_purchase, 2),
            'total_deposit': round(total_deposit_sales - total_deposit_purchase, 2),
            'total_credit': round(total_credit_sales - total_credit_purchase, 2),
        }
        total.append(new_total)
        return total


def get_sales_credit_list(request):
    if request.method == 'GET':
        start_date = request.GET.get('_init', '')
        end_date = request.GET.get('_end', '')
        if start_date != '' and end_date != '':
            user_id = request.user.id
            user_obj = User.objects.get(id=int(user_id))
            subsidiary_obj = get_subsidiary_by_user(user_obj)
            orders_set = Order.objects.filter(create_at__range=(start_date, end_date), type='V', status='C',
                                              subsidiary=subsidiary_obj, payments__type_payment='C',
                                              payments__amount__gt=0)
            tpl_list = loader.get_template('accounting/sales_credit_grid_list.html')
            context = ({'orders_set': orders_set, })

            return JsonResponse({
                'message': 'Creditos disponibles',
                'grid': tpl_list.render(context),
            }, status=HTTPStatus.OK)
        else:
            my_date = datetime.now()
            date_now = my_date.strftime("%Y-%m-%d")
            client_set = Client.objects.filter(order__payments__type_payment='C', order__payments__amount__gt=0).values(
                'id', 'full_names')
            return render(request, 'accounting/sales_credit_list.html', {
                'date_now': date_now,
                'client_set': client_set,
            })


def get_sales_credit_by_client(request):
    if request.method == 'GET':
        pk = request.GET.get('client_pk', '')
        if pk != '':
            client_obj = Client.objects.get(id=int(pk))
            user_id = request.user.id
            user_obj = User.objects.get(id=int(user_id))
            subsidiary_obj = get_subsidiary_by_user(user_obj)
            orders_set = Order.objects.filter(type='V', status='C',
                                              subsidiary=subsidiary_obj, client=client_obj, payments__type_payment='C',
                                              payments__amount__gt=0)
            tpl_list = loader.get_template('accounting/sales_credit_grid_list.html')
            context = ({'orders_set': orders_set, })
            return JsonResponse({
                'message': 'Deuda de ventas',
                'grid': tpl_list.render(context),
            }, status=HTTPStatus.OK)


def get_sales_credit_detail(request):
    if request.method == 'GET':
        id_order = request.GET.get('pk', '')
        order_obj = Order.objects.get(pk=int(id_order))
        payment_set = Payments.objects.filter(order=order_obj, type='I', type_payment='C', amount__gt=0)
        t = loader.get_template('accounting/sales_payment_grid.html')
        c = ({
            'payment_set': payment_set,
        })
        return JsonResponse({
            'grid': t.render(c, request),
        }, status=HTTPStatus.OK)


def get_modal_payment_credit(request):
    if request.method == 'GET':
        payment_pk = request.GET.get('pk', '')
        payment_obj = Payments.objects.get(id=int(payment_pk))
        date_ = datetime.now()
        date_now = date_.strftime("%Y-%m-%d")
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        casing_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj).values('id',
                                                                                              'name')
        coin_set = Coin.objects.all().order_by('id')
        t = loader.get_template('accounting/modal_payment_credit.html')
        c = ({
            'payment_obj': payment_obj,
            'date_now': date_now,
            'type_payment': Payments._meta.get_field('type_payment').choices,
            'casing_set': casing_set,
            'coin_set': coin_set,
            'bank_set': Payments._meta.get_field('type_bank').choices,
        })
        return JsonResponse({
            'form': t.render(c, request),
        })


@csrf_exempt
def payment_credit(request):
    if request.method == 'POST':
        payment_pk = request.POST.get('id-payment', '')
        payment_obj = Payments.objects.get(id=int(payment_pk))
        coin_pk = request.POST.get('id-coin', '')
        coin_obj = Coin.objects.get(id=int(coin_pk))
        type_payment = request.POST.get('id-type-payment', '')
        date_payment = request.POST.get('id-date-payment', '')
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        if type_payment == 'E':
            cash_pk = request.POST.get('id-cash', '')
            cash_obj = Casing.objects.get(id=int(cash_pk))
            amount_cash = decimal.Decimal(request.POST.get('id-amount-cash', ''))
            new_payment_e = {
                'order': payment_obj.order,
                'type': 'I',
                'type_payment': type_payment,
                'amount': amount_cash,
                'coin': coin_obj,
                'date_payment': date_payment,
                'user': user_obj,
                'subsidiary': subsidiary_obj,
                'casing': cash_obj,
            }
            new_payment_e_obj = Payments.objects.create(**new_payment_e)
            new_payment_e_obj.save()
            payment_obj.amount = payment_obj.amount - amount_cash
            payment_obj.save()
        elif type_payment == 'D':
            bank_pk = request.POST.get('id-deposit', '')
            amount_deposit = decimal.Decimal(request.POST.get('id-amount-deposit', ''))
            code_operation = str(request.POST.get('id-code-operation', ''))
            new_payment_d = {
                'order': payment_obj.order,
                'type': 'I',
                'type_payment': type_payment,
                'type_bank': bank_pk,
                'code_operation': code_operation,
                'amount': amount_deposit,
                'coin': coin_obj,
                'date_payment': date_payment,
                'user': user_obj,
                'subsidiary': subsidiary_obj,
            }
            new_payment_d_obj = Payments.objects.create(**new_payment_d)
            new_payment_d_obj.save()
            payment_obj.amount = payment_obj.amount - amount_deposit
            payment_obj.save()

        return JsonResponse({
            'success': True,
        }, status=HTTPStatus.OK)


def get_payment_list(request):
    if request.method == 'GET':
        start_date = request.GET.get('_init', '')
        if start_date != '':
            user_id = request.user.id
            user_obj = User.objects.get(id=int(user_id))
            subsidiary_obj = get_subsidiary_by_user(user_obj)
            payment_set = Payments.objects.filter(date_payment__date=start_date,
                                                  subsidiary=subsidiary_obj).exclude(type='E')
            tpl_list = loader.get_template('accounting/payment_grid_list.html')
            context = ({'payment_set': payment_set, })

            return JsonResponse({
                'message': 'Detalle de pagos',
                'grid': tpl_list.render(context),
            }, status=HTTPStatus.OK)
        else:
            my_date = datetime.now()
            date_now = my_date.strftime("%Y-%m-%d")
            return render(request, 'accounting/payment_list.html', {
                'date_now': date_now,
            })
