from django.contrib import admin
from apps.purchase import models

# Register your models here.
from apps.purchase.models import Provider

admin.site.register(Provider)
