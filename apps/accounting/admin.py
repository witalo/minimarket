from django.contrib import admin

# Register your models here.
from apps.accounting.models import Casing


class CasingAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'type', 'is_enabled', 'user', 'subsidiary']
    ordering = ('id',)


admin.site.register(Casing, CasingAdmin)