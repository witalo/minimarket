from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Adjust


# Create your models here.

class Employee(models.Model):
    GENDER_CHOICES = (('1', 'Masculino'), ('2', 'Femenino'),)
    OCCUPATION_CHOICES = (('1', 'Administrador'), ('2', 'Gerente General'), ('3', 'Gerente de Recursos Humanos'), ('4', 'Gerente de Operacione'), ('5', 'Gerente de Logística'), ('6', 'Gerente Financiero'), ('7', 'Gerente Comercial'),('8', 'Gerente de Marketing'), ('9', 'Cajero'), ('10', 'Mesero '), ('11', 'Sin Asignar'))
    id = models.AutoField(primary_key=True)
    document_number = models.CharField(max_length=15, null=True, blank=True)
    birth_date = models.DateField('Fecha de nacimiento', null=True, blank=True)
    paternal_last_name = models.CharField(max_length=40, null=True, blank=True)
    maternal_last_name = models.CharField(max_length=40, null=True, blank=True)
    names = models.CharField(max_length=40, null=True, blank=True)
    gender = models.CharField('Sexo', max_length=1, choices=GENDER_CHOICES, default='1', )
    telephone_number = models.CharField(max_length=9, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    address = models.CharField('Direccion', max_length=200, null=True, blank=True)
    subsidiary = models.ForeignKey('Subsidiary', on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ImageField(upload_to='employee/',
                              default='employee/employee0.jpg', blank=True)
    photo_thumbnail = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1), ResizeToFill(
        100, 100)], source='photo', format='JPEG', options={'quality': 90})
    user = models.ForeignKey(User, verbose_name='Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    occupation = models.CharField('Ocupacion', max_length=50, choices=OCCUPATION_CHOICES, default='11', )
    is_state = models.BooleanField('Estado', default=False)

    def _str_(self):
        return str(self.names)

    def full_name(self):
        # return str(self.names) + ' ' + str(self.paternal_last_name) + ' ' + str(self.maternal_last_name)
        return '{} {} {}'.format(self.names, self.paternal_last_name, self.maternal_last_name)

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'


class Subsidiary(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    serial = models.CharField(max_length=4, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=45, null=True, blank=True)
    ruc = models.CharField(max_length=11)
    business_name = models.CharField('Razón social', max_length=45, null=True, blank=True)
    legal_representative_name = models.CharField(max_length=100, null=True, blank=True)
    legal_representative_dni = models.CharField(max_length=45, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Filial'
        verbose_name_plural = 'Filiales'