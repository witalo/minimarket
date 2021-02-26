from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('create_user/', login_required(create_user), name='create_user'),
    path('update_user/', login_required(update_user), name='update_user'),
]