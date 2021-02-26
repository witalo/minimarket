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
    SubsidiaryStore


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


def get_opening_casing(request):
    if request.method == 'GET':
        operation = request.GET.get('operation', '')
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        casing_set = Casing.objects.filter(user=user_obj, is_enabled=True, subsidiary=subsidiary_obj).values('id',
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
        }, status=HTTPStatus.OK)


def get_validate_aperture(request):
    data = dict()
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
                    data['error'] = "Cierre la caja antes de aperturar una nueva"
                    response = JsonResponse(data)
                    response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                    return response
            else:
                data['error'] = "Cierre la caja antes de aperturar una nueva"
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response

    return JsonResponse({
        'success': True,
    }, status=HTTPStatus.OK)


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


def get_closing_casing(request):
    if request.method == 'GET':
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        casing_set = Casing.objects.filter(user=user_obj, is_enabled=True, subsidiary=subsidiary_obj).values('id',
                                                                                                             'name')
        tpl = loader.get_template('accounting/closing_casing.html')
        context = ({
            'date_now': date_now,
            'casing_set': casing_set,
        })

        return JsonResponse({
            'grid': tpl.render(context),
        }, status=HTTPStatus.OK)


@csrf_exempt
def closing_casing_c(request):
    if request.method == 'POST':
        _date = request.POST.get('date-closing', '')
        _cashing_pk = request.POST.get('closing-cash', '')
        _amount_aperture = (request.POST.get('amount-aperture-closing-casing', ''))
        _amount_cash = (request.POST.get('amount-cash-closing-casing', ''))
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
            'message': 'Gracias por cerrar la caja',
        }, status=HTTPStatus.OK)


def get_total_casing(request):
    data = dict()
    if request.method == 'GET':
        total_aperture = decimal.Decimal(0.00)
        total_cash = decimal.Decimal(0.00)
        total_deposit = decimal.Decimal(0.00)
        total_credit = decimal.Decimal(0.00)
        pk = request.GET.get('pk_cash', '')
        date_closing = request.GET.get('date_closing', '')
        casing_obj = Casing.objects.get(id=int(pk))
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = get_subsidiary_by_user(user_obj)
        try:
            payment_aperture_obj = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj,
                                                           type_payment='E', type='A').last()
            if payment_aperture_obj is not None:
                total_aperture = payment_aperture_obj.amount
        except Payments.DoesNotExist:
            data['error'] = "La caja no se encuentra aperturada, no puede hacer cierre de caja"
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
                if payment_closing_obj.id >= payment_aperture_obj.id:
                    data['error'] = "La caja no se encuentra aperturada, no puede hacer cierre de caja"
                    response = JsonResponse(data)
                    response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                    return response

        if payment_aperture_obj is not None:
            payment_total_cash = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj,
                                                         type_payment='E', type='I',
                                                         create_at__gte=payment_aperture_obj.create_at).aggregate(
                Sum('amount'))
            if payment_total_cash is not None:
                total_cash = payment_total_cash['amount__sum']
            payment_total_deposit = Payments.objects.filter(user=user_obj, subsidiary=subsidiary_obj,
                                                            type_payment='D', type='I',
                                                            create_at__gte=payment_aperture_obj.create_at).aggregate(
                Sum('amount'))
            if payment_total_deposit is not None:
                total_deposit = payment_total_deposit['amount__sum']
            payment_total_credit = Payments.objects.filter(user=user_obj, subsidiary=subsidiary_obj,
                                                           type_payment='C', type='I',
                                                           create_at__gte=payment_aperture_obj.create_at).aggregate(
                Sum('amount'))
            if payment_total_credit is not None:
                total_credit = payment_total_credit['amount__sum']
        else:
            data['error'] = "La caja no se encuentra aperturada, no puede hacer cierre de cajas sin aperturar"
            response = JsonResponse(data)
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return response
        return JsonResponse({
            'total_aperture': total_aperture,
            'total_cash': total_cash,
            'total_deposit': total_deposit,
            'total_credit': total_credit,
        }, status=HTTPStatus.OK)
