from django.db import models
from django.contrib.auth.models import User

from apps.hrm.models import Subsidiary
from apps.sale.models import Order


class Casing(models.Model):
    TYPE_CHOICES = (('G', 'General'), ('C', 'Chica'))
    id = models.AutoField(primary_key=True)
    name = models.CharField('Nombre caja', max_length=50)
    description = models.CharField('Descripción', max_length=100, null=True, blank=True)
    type = models.CharField('Tipo caja', max_length=1, choices=TYPE_CHOICES)
    is_enabled = models.BooleanField(default=True)
    subsidiary = models.ForeignKey(Subsidiary, on_delete=models.SET_NULL, null=True, blank=True)
    create_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'


class Payments(models.Model):
    TYPE_CHOICES = (('I', 'Ingreso'), ('E', 'Egreso'), ('A', 'Apertura'), ('C', 'Cierre'))
    TYPE_PAYMENT = (('E', 'Efectivo'), ('D', 'Deposito'), ('C', 'Credito'))
    TYPE_BANK = (('1', 'Banco de Credito del Peru'), ('2', 'Banco de la Nación del Peru'), ('3', 'Interbank'),
                 ('4', 'BBVA Continental'))
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField('Tipo proceso', max_length=1, choices=TYPE_CHOICES)
    type_payment = models.CharField('Tipo proceso', max_length=1, choices=TYPE_PAYMENT)
    type_bank = models.CharField('Banco', max_length=1, choices=TYPE_BANK, null=True, blank=True)
    code_operation = models.CharField('Coidgo de operacion', max_length=50, null=True, blank=True)
    amount = models.DecimalField('Monto de pago', max_digits=10, decimal_places=2, default=0)
    coin = models.ForeignKey('sale.Coin', on_delete=models.CASCADE, null=True, blank=True)
    date_payment = models.DateTimeField(null=True, blank=True)
    create_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, verbose_name='Usuario', on_delete=models.CASCADE)
    subsidiary = models.ForeignKey(Subsidiary, on_delete=models.SET_NULL, null=True, blank=True)
    casing = models.ForeignKey(Casing, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Registro de pago'
        verbose_name_plural = 'Registros de pagos'
