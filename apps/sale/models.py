from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Adjust
from django.db.models import Min, Sum

from apps import purchase
from apps.hrm.models import Subsidiary


class Client(models.Model):
    DOCUMENT_TYPE = (('01', 'DNI'), ('06', 'RUC'), ('07', 'PASAPORTE'), ('04', 'CARNET DE EXTRANJERÍA'))
    id = models.AutoField(primary_key=True)
    type_document = models.CharField('Tipo Documento', max_length=2, choices=DOCUMENT_TYPE, default='01', )
    document = models.CharField(max_length=15, null=True, blank=True)
    full_names = models.CharField(max_length=200, null=True, blank=True)
    telephone_number = models.CharField(max_length=9, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    address = models.CharField('Direccion', max_length=200, null=True, blank=True)

    def _str_(self):
        return str(self.full_names)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'


class Product(models.Model):
    TYPE_CHOICES = (
        ('1', 'Bienes de uso común'), ('2', 'Bienes de consumo'), ('3', 'Bienes de emergencia'),
        ('4', 'Bienes durables'),
        ('5', 'Bienes de especialidad'), ('6', 'Servicios'),)
    id = models.AutoField(primary_key=True)
    code = models.CharField('Codigo', max_length=50, null=True, blank=True)
    names = models.CharField('Nombre', max_length=100, unique=True)
    stock_min = models.DecimalField('Stock Minimo', max_digits=30, decimal_places=2, default=0)
    stock_max = models.DecimalField('Stock Maximo', max_digits=30, decimal_places=2, default=0)
    product_category = models.ForeignKey('ProductCategory', on_delete=models.CASCADE)
    type = models.CharField('Tipo', max_length=1, choices=TYPE_CHOICES, default='1')
    photo = models.ImageField(upload_to='product/',
                              default='product/product0.jpg', blank=True)
    photo_thumbnail = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1), ResizeToFill(
        100, 100)], source='photo', format='JPEG', options={'quality': 90})
    is_state = models.BooleanField('Estado', default=True)

    def _str_(self):
        return str(self.names)

    class Meta:
        unique_together = ('names','code')
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


class ProductCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Nombre', max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'


class ProductPresenting(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)
    coin = models.ForeignKey('Coin', on_delete=models.CASCADE)
    price_sale = models.DecimalField('Precio de Venta', max_digits=30, decimal_places=2, default=0)
    quantity_minimum = models.DecimalField('Cantidad Minima', max_digits=30, decimal_places=2, default=0)
    code = models.CharField('Codigo', max_length=100, null=True, blank=True)
    is_enabled = models.BooleanField('Habilitado', default=True)

    def __str__(self):
        return str(self.product.name) + " - " + str(self.unit.name)

    def get_price_sale_with_dot(self):
        return str(self.price_sale).replace(',', '.')

    def get_quantity_minimum_with_dot(self):
        return str(self.quantity_minimum).replace(',', '.')

    class Meta:
        unique_together = ('product', 'unit', 'coin')
        verbose_name = 'Presentación'
        verbose_name_plural = 'Presentaciones'


class Unit(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Nombre', max_length=5, unique=True)
    description = models.CharField('Descripción', max_length=50, null=True, blank=True)
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Unidad de medida'
        verbose_name_plural = 'Unidades de medida'


class Coin(models.Model):
    id = models.AutoField(primary_key=True)
    name_coin = models.CharField('Nombre moneda', max_length=50, unique=True)
    abbreviation = models.CharField('Abreviatura', max_length=5, null=True, blank=True)
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name_coin

    class Meta:
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'


class SubsidiaryStore(models.Model):
    CATEGORY_CHOICES = (
        ('1', 'Materias primas'), ('2', 'Productos intermedios'), ('3', 'Productos terminados'), ('4', 'Equipos'),
        ('5', 'Accesorios'),)
    id = models.AutoField(primary_key=True)
    subsidiary = models.ForeignKey(Subsidiary, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField('Nombre', max_length=50)
    category = models.CharField('Categoria', max_length=1, choices=CATEGORY_CHOICES, default='1')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('subsidiary', 'category',)
        verbose_name = 'Almacén de sede'
        verbose_name_plural = 'Almacenes de sede'


class ProductStore(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product', verbose_name='Producto', on_delete=models.CASCADE)
    subsidiary_store = models.ForeignKey('SubsidiaryStore', verbose_name='Almacen sede', on_delete=models.CASCADE,
                                         related_name='stores')
    stock = models.DecimalField('Stock', max_digits=30, decimal_places=4, default=0)

    def __str__(self):
        return self.product.names

    def get_stock_with_dot(self):
        return str(self.stock).replace(',', '.')

    class Meta:
        unique_together = ('product', 'subsidiary_store',)
        verbose_name = 'Almacén de producto'
        verbose_name_plural = 'Almacenes de producto'


class Kardex(models.Model):
    OPERATION_CHOICES = (('C', 'Inicial'), ('E', 'Entrada'), ('S', 'Salida'), ('R', 'Reajuste'))
    id = models.AutoField(primary_key=True)
    operation = models.CharField('Operación', max_length=1,
                                 choices=OPERATION_CHOICES, default='C', )
    quantity = models.DecimalField('Cantidad', max_digits=10, decimal_places=2, default=0)
    price_unit = models.DecimalField('Precio unitario', max_digits=30, decimal_places=15, default=0)
    price_total = models.DecimalField('Precio total', max_digits=30, decimal_places=15, default=0)
    remaining_quantity = models.DecimalField('Cantidad restante', max_digits=10, decimal_places=2, default=0)
    product_store = models.ForeignKey(
        'ProductStore', on_delete=models.SET_NULL, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    order_detail = models.ForeignKey('OrderDetail', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Registro de Kardex'
        verbose_name_plural = 'Registros de Kardex'


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    TYPE_CHOICES = (('T', 'Cotización'), ('V', 'Venta'), ('R', 'Requerimiento'), ('C', 'Compra'), ('F', 'Fabricacion'))
    STATUS_CHOICES = (('P', 'Pendiente'), ('C', 'Completado'), ('A', 'Anulado'),)
    type = models.CharField('Tipo', max_length=1, choices=TYPE_CHOICES, default='T', )
    provider = models.ForeignKey('purchase.Provider', verbose_name='Proveedor',
                                 on_delete=models.SET_NULL, null=True, blank=True)
    invoice = models.CharField('Comprobante', max_length=100, null=True, blank=True)
    correlative_order = models.IntegerField('Correlativo de la orden', default=0)
    status = models.CharField('Estado', max_length=1, choices=STATUS_CHOICES, default='P', )
    create_at = models.DateTimeField(null=True, blank=True)
    update_at = models.DateTimeField(auto_now=True)
    client = models.ForeignKey('Client', verbose_name='Cliente',
                               on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, verbose_name='Usuario', on_delete=models.CASCADE)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField('Descuento', max_digits=10, decimal_places=2, default=0)
    subsidiary = models.ForeignKey(Subsidiary, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id) + " / " + str(self.create_at)

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'


class OrderDetail(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.DecimalField('Cantidad', max_digits=10, decimal_places=2, default=0)
    price_unit = models.DecimalField('Precio unitario', max_digits=10, decimal_places=2, default=0)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.product.code)

    class Meta:
        verbose_name = 'Detalle venta'
        verbose_name_plural = 'Detalles venta'


class OrderBill(models.Model):
    STATUS_CHOICES = (('E', 'Emitido'), ('A', 'Anulado'),)
    TYPE_CHOICES = (('1', 'Factura'), ('2', 'Boleta'),)
    order = models.OneToOneField('Order', on_delete=models.CASCADE, primary_key=True)
    type = models.CharField('Tipo de Comprobante', max_length=2, choices=TYPE_CHOICES)
    serial = models.CharField('Serie', max_length=5, null=True, blank=True)
    number_receipt = models.IntegerField('Numero de Comprobante', default=0)
    sunat_status = models.CharField('Sunat Status', max_length=5, null=True, blank=True)
    sunat_description = models.CharField('Sunat descripcion', max_length=50, null=True, blank=True)
    user = models.ForeignKey(User, verbose_name='Usuario', on_delete=models.CASCADE)
    sunat_enlace_pdf = models.CharField('Sunat Enlace Pdf', max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    code_qr = models.CharField('Codigo QR', max_length=500, null=True, blank=True)
    code_hash = models.CharField('Codigo Hash', max_length=500, null=True, blank=True)
    status = models.CharField('Estado', max_length=1, choices=STATUS_CHOICES)

    def __str__(self):
        return str(self.order.id)

    class Meta:
        verbose_name = 'Registro de comprobante'
        verbose_name_plural = 'Registros de comprobantes'


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='recipe')
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    subsidiary = models.ForeignKey(Subsidiary, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Registro de Receta'
        verbose_name_plural = 'Registros de Recetas'


class RecipeDetail(models.Model):
    id = models.AutoField(primary_key=True)
    product_input = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='inputs')
    quantity = models.DecimalField('Cantidad', max_digits=10, decimal_places=2, default=0)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)
    price = models.DecimalField('Precio Unitario', max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Detalle de Receta'
        verbose_name_plural = 'Detalles de Recetas'


