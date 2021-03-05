from django.urls import path, include
from .views import *
from .views_PDF import print_ticket_order_sales
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Client
    path('client_list/', login_required(get_client_list), name='client_list'),
    path('get_client_form/', login_required(get_client_form), name='get_client_form'),
    path('save_client/', login_required(save_client), name='save_client'),
    path('update_client/', login_required(update_client), name='update_client'),
    path('get_client_update_form/', login_required(get_client_update_form), name='get_client_update_form'),
    # Product
    path('product_list/', login_required(get_product_view), name='product_list'),
    path('get_product_by_condition/', login_required(get_product_by_condition), name='get_product_by_condition'),
    path('product_form/', login_required(get_product_form), name='product_product'),
    path('save_product/', login_required(save_product), name='save_product'),
    path('update_product/', login_required(update_product), name='update_product'),
    path('get_product_update_form/', login_required(get_product_update_form), name='get_product_update_form'),
    # Product presenting
    path('product_presenting_operation/', login_required(product_presenting_operation), name='product_presenting_operation'),
    path('update_product_presenting/', login_required(update_product_presenting), name='update_product_presenting'),
    path('set_code_presenting/', login_required(set_code_presenting), name='set_code_presenting'),
    path('get_product_presenting/', login_required(get_product_presenting), name='get_product_presenting'),
    path('status_product_presenting/', login_required(status_product_presenting), name='status_product_presenting'),
    path('delete_product_presenting/', login_required(delete_product_presenting), name='delete_product_presenting'),
    # Stock initial product
    path('template_initial_stock/', login_required(get_template_initial), name='template_initial_stock'),
    path('get_template_initial/', login_required(get_template_initial), name='get_template_initial'),
    path('update_product_store_by_subsidiary_store/', login_required(update_product_store_by_subsidiary_store),
         name='update_product_store_by_subsidiary_store'),
    # Kardex product
    path('get_kardex_by_product/', login_required(get_kardex_by_product), name='get_kardex_by_product'),
    path('get_list_kardex/', login_required(get_list_kardex), name='get_list_kardex'),
    # orders sales
    path('order_sales/', login_required(get_order_sales), name='order_sales'),
    path('get_client_by_document/', login_required(get_client_by_document), name='get_client_by_document'),
    path('save_client_order/', login_required(save_client_order), name='save_client_order'),
    path('get_prices_by_product/', login_required(get_prices_by_product), name='get_prices_by_product'),
    path('create_order_sales/', login_required(create_order_sales), name='create_order_sales'),
    # generate PDF
    path('print_ticket_order_sales/<int:pk>/', login_required(print_ticket_order_sales), name='print_ticket_order_sales'),
    # reports
    path('order_sales_list/', login_required(get_order_sales_list), name='order_sales_list'),
    path('get_sales_detail/', login_required(get_sales_detail), name='get_sales_detail'),
    path('get_order_sales_by_client/', login_required(get_order_sales_by_client), name='get_order_sales_by_client'),

]
