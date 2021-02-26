from django.contrib import admin
from apps.sale import models

from .models import Product, ProductCategory, SubsidiaryStore, ProductStore, Unit, Coin


class ProductCategoryAdmin(admin.ModelAdmin):
    fields = ['name']
    ordering = ('id',)


admin.site.register(ProductCategory, ProductCategoryAdmin)


class UnitAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'is_enabled']
    ordering = ('id',)


admin.site.register(Unit, UnitAdmin)


class CoinAdmin(admin.ModelAdmin):
    fields = ['name_coin', 'abbreviation', 'is_enabled']
    ordering = ('id',)


admin.site.register(Coin, CoinAdmin)


class SubsidiaryStoreAdmin(admin.ModelAdmin):
    fields = ['name', 'subsidiary', 'category']
    ordering = ('id',)


admin.site.register(SubsidiaryStore, SubsidiaryStoreAdmin)


class ProductAdmin(admin.ModelAdmin):
    fields = ['code', 'names', 'stock_min', 'stock_max', 'photo', 'is_state', 'product_category', 'type']
    ordering = ('id',)


admin.site.register(Product, ProductAdmin)


class ProductStoreAdmin(admin.ModelAdmin):
    fields = ['stock', 'product', 'subsidiary_store']
    ordering = ('id',)


admin.site.register(ProductStore, ProductStoreAdmin)





