from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Adjust
from django.db.models import Min, Sum


# Create your models here.
class Provider(models.Model):
    DOCUMENT_TYPE = (('01', 'DNI'), ('06', 'RUC'))
    id = models.AutoField(primary_key=True)
    type_document = models.CharField('Tipo Documento', max_length=2, choices=DOCUMENT_TYPE, default='01', )
    document = models.CharField(max_length=15, null=True, blank=True)
    full_names = models.CharField(max_length=200, null=True, blank=True)
    telephone = models.CharField(max_length=9, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    address = models.CharField('Direccion', max_length=200, null=True, blank=True)

    def _str_(self):
        return str(self.full_names)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
