from datetime import datetime
from http import HTTPStatus
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.template import loader
from apps.hrm.models import Employee, Subsidiary


class Home(TemplateView):
    template_name = 'index.html'


def get_report(request):
    return render(request, 'hrm/charts.html', {
    })


# lista de empleados
def get_employee_list(request):
    if request.method == 'GET':
        employee_set = Employee.objects.all()
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m")
        return render(request, 'hrm/employee_list.html', {
            'date_now': date_now,
            'employee_set': employee_set,
        })


# abrir el formulario de registro
def get_employee_form(request):
    if request.method == 'GET':
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")

        t = loader.get_template('hrm/employee_form.html')
        c = ({
            'date_now': date_now,
            'type_gender': Employee._meta.get_field('gender').choices,
            'type_occupation': Employee._meta.get_field('occupation').choices,
        })
        return JsonResponse({
            'form': t.render(c, request),
        })


# registrar empleado
@csrf_exempt
def save_employee(request):
    if request.method == 'POST':
        _document = request.POST.get('document', '')
        _birth_date = request.POST.get('birth_date', '')
        _paternal_last_name = request.POST.get('paternal', '')
        _maternal_last_name = request.POST.get('maternal', '')
        _names = request.POST.get('names', '')
        _gender_id = request.POST.get('gender', '')
        _occupation_id = request.POST.get('occupation', '')
        _telephone_number = request.POST.get('telephone', '')
        _email = request.POST.get('email', '')
        _address = request.POST.get('address', '')
        _state = bool(request.POST.get('checkbox', ''))
        try:
            _photo = request.FILES['customFile']
        except Exception as e:
            _photo = 'employee/employee0.jpg'

        employee_obj = Employee(
            document_number=_document,
            birth_date=_birth_date,
            paternal_last_name=_paternal_last_name,
            maternal_last_name=_maternal_last_name,
            names=_names,
            gender=_gender_id,
            telephone_number=_telephone_number,
            email=_email,
            address=_address,
            occupation=_occupation_id,
            is_state=_state,
            photo=_photo,
        )
        employee_obj.save()
        return JsonResponse({
            'success': True,
        }, status=HTTPStatus.OK)


# renderizar datos del empleado
def get_employee_by_id(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        employee_obj = Employee.objects.get(id=pk)
        subsidiary_set = Subsidiary.objects.all()
        t = loader.get_template('hrm/employee_subsidiary.html')
        c = ({
            'employee_obj': employee_obj,
            'subsidiary_set': subsidiary_set,
        })
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


# actualizar sucursal del empleado
@csrf_exempt
def update_subsidiary_employee(request):
    if request.method == 'POST':
        _id = int(request.POST.get('pk', ''))
        employee_obj = Employee.objects.get(id=_id)
        _id_subsidiary = int(request.POST.get('subsidiary', ''))
        subsidiary_obj = Subsidiary.objects.get(id=_id_subsidiary)
        employee_obj.subsidiary = subsidiary_obj
        employee_obj.save()
        return JsonResponse({
            'success': True,
        }, status=HTTPStatus.OK)


# renderizar datos para la creacion de trabajo-usuario
def get_create_user(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        employee_obj = Employee.objects.get(id=pk)
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        t = loader.get_template('hrm/create_user.html')
        c = ({
            'employee_obj': employee_obj,
            'date_now': date_now,
        })
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


# renderizar datos para la actualizacion de trabajo-usuario
def get_update_user(request):
    if request.method == 'GET':
        pk = int(request.GET.get('pk', ''))
        user_obj = User.objects.get(id=pk)
        employee_obj = Employee.objects.get(user=user_obj)
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        t = loader.get_template('hrm/update_user.html')
        c = ({
            'employee_obj': employee_obj,
            'date_now': date_now,
        })
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


# renderizar datos para la actualizacion de trabajo-usuario
def get_employee_update_form(request):
    if request.method == 'GET':
        pk = int(request.GET.get('pk', ''))
        employee_obj = Employee.objects.get(id=pk)
        t = loader.get_template('hrm/employee_update_form.html')
        c = ({
            'employee_obj': employee_obj,
            'type_gender': Employee._meta.get_field('gender').choices,
            'type_occupation': Employee._meta.get_field('occupation').choices,
        })
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


# registrar empleado
@csrf_exempt
def update_employee(request):
    if request.method == 'POST':
        _id = int(request.POST.get('pk', ''))
        employee_obj = Employee.objects.get(id=_id)
        _document = request.POST.get('document', '')
        _birth_date = request.POST.get('birth_date', '')
        _paternal_last_name = request.POST.get('paternal', '')
        _maternal_last_name = request.POST.get('maternal', '')
        _names = request.POST.get('names', '')
        _gender_id = request.POST.get('gender', '')
        _occupation_id = request.POST.get('occupation', '')
        _telephone_number = request.POST.get('telephone', '')
        _email = request.POST.get('email', '')
        _address = request.POST.get('address', '')
        _photo = request.FILES.get('customFile', False)
        _state = bool(request.POST.get('checkbox', ''))

        employee_obj.document_number = _document
        employee_obj.birth_date = _birth_date
        employee_obj.paternal_last_name = _paternal_last_name
        employee_obj.maternal_last_name = _maternal_last_name
        employee_obj.names = _names
        employee_obj.gender = _gender_id
        employee_obj.occupation = _occupation_id
        employee_obj.telephone_number = _telephone_number
        employee_obj.email = _email
        employee_obj.address = _address
        if _photo is not False:
            employee_obj.photo = _photo
        employee_obj.is_state = _state
        employee_obj.save()
        return JsonResponse({
            'success': True,
        }, status=HTTPStatus.OK)


# retorna la sucursal
def get_subsidiary_by_user(user_obj):
    employee_obj = Employee.objects.get(user=user_obj)
    if employee_obj.subsidiary:
        subsidiary = employee_obj.subsidiary
    return subsidiary
