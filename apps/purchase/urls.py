from django.contrib.auth.decorators import login_required
from django.urls import path, include
from .views import *

# from .views_PDF import print_ticket_order_sales

urlpatterns = [

    # orders purchase
    path('order_purchase/', login_required(get_order_purchase), name='order_purchase'),
    path('get_details_purchase/', login_required(get_details_purchase), name='get_details_purchase'),
    path('create_order_purchase/', login_required(create_order_purchase), name='create_order_purchase'),
    path('get_units_and_store_by_product/', login_required(get_units_and_store_by_product),
         name='get_units_and_store_by_product'),
    # provider
    path('provider_list/', login_required(get_provider_list), name='provider_list'),
    path('get_provider_form/', login_required(get_provider_form), name='get_provider_form'),
    path('save_provider/', login_required(save_provider), name='save_provider'),
    path('get_provider_update_form/', login_required(get_provider_update_form), name='get_provider_update_form'),
    path('update_provider/', login_required(update_provider), name='update_provider'),

    # Graphic
    path('graphic_sales_purchase/', login_required(graphic_sales_purchase), name='graphic_sales_purchase'),
    path('graphic_sales_purchase_view/', login_required(graphic_sales_purchase_view),
         name='graphic_sales_purchase_view'),

]
