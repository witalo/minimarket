from django.urls import path, include
from .views import *

# from .views_PDF import print_ticket_order_sales

urlpatterns = [

    # orders purchase
    path('order_purchase/', get_order_purchase, name='order_purchase'),
    path('get_details_purchase/', get_details_purchase, name='get_details_purchase'),
    path('create_order_purchase/', create_order_purchase, name='create_order_purchase'),
    path('get_units_and_store_by_product/', get_units_and_store_by_product, name='get_units_and_store_by_product'),
    # provider
    path('provider_list/', get_provider_list, name='provider_list'),
    path('get_provider_form/', get_provider_form, name='get_provider_form'),
    path('save_provider/', save_provider, name='save_provider'),
    path('get_provider_update_form/', get_provider_update_form, name='get_provider_update_form'),
    path('update_provider/', update_provider, name='update_provider'),

]
