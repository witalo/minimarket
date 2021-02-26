from http import HTTPStatus

from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect, JsonResponse
from .forms import FormLogin
from ..hrm.models import Employee


class Login(FormView):
    template_name = 'login.html'
    form_class = FormLogin
    success_url = reverse_lazy('home')

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(Login, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(Login, self).form_valid(form)


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/accounts/login/')


# creacion de usuario
@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        _id = int(request.POST.get('pk'))
        employee_obj = Employee.objects.get(id=_id)
        _username = request.POST.get('username')
        _password = request.POST.get('password')
        _user_email = _username + '@system.com'
        is_staff = False
        if request.POST.get('is_staff') is not None:
            is_staff = bool(request.POST.get('is_staff'))

        if _username != '':
            try:
                user_obj = User.objects.get(username=_username)
            except User.DoesNotExist:
                user_obj = None

            if user_obj is not None:
                response = JsonResponse({'error': "Este usuario ya existe."})
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response

            user_obj = User(
                username=_username,
                email=_user_email,
            )
            user_obj.set_password(_password)
            user_obj.is_staff = is_staff
            user_obj.save()
            if user_obj.id != '':
                employee_obj.user = user_obj
                employee_obj.save()
            return JsonResponse({
                'success': True,
            }, status=HTTPStatus.OK)


# creacion de usuario
@csrf_exempt
def update_user(request):
    if request.method == 'POST':
        _id = int(request.POST.get('pk'))
        user_obj = User.objects.get(id=_id)
        _username = request.POST.get('username')
        _password = request.POST.get('password')
        is_staff = False
        if request.POST.get('is_staff') is not None:
            is_staff = bool(request.POST.get('is_staff'))

        if _username != '':
            try:
                _search = User.objects.get(username=_username).id
            except User.DoesNotExist:
                _search = None
        if _search is not None:
            if _search != user_obj.id:
                response = JsonResponse({'error': "Este usuario ya existe."})
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response

        user_obj.username = _username
        user_obj.set_password(_password)
        user_obj.is_staff = is_staff
        user_obj.save()
        return JsonResponse({
            'success': True,
        }, status=HTTPStatus.OK)
