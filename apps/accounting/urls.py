from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required
from .views_PDF import print_ticket_closing_cash

urlpatterns = [
    # Opening casing
    path('get_valid_opening_cash/', login_required(get_valid_opening_cash), name='get_valid_opening_cash'),
    path('get_opening_casing/', login_required(get_opening_casing), name='get_opening_casing'),
    path('opening_casing_a/', login_required(opening_casing_a), name='opening_casing_a'),
    path('get_validate_aperture/', login_required(get_validate_aperture), name='get_validate_aperture'),
    path('get_closing_casing/', login_required(get_closing_casing), name='get_closing_casing'),
    path('closing_casing_c/', login_required(closing_casing_c), name='closing_casing_c'),
    path('get_total_casing/', login_required(get_total_casing), name='get_total_casing'),
    # report credit
    path('sales_credit_list/', login_required(get_sales_credit_list), name='sales_credit_list'),
    path('sales_credit_by_client/', login_required(get_sales_credit_by_client), name='sales_credit_by_client'),
    path('sales_credit_detail/', login_required(get_sales_credit_detail), name='sales_credit_detail'),
    # payment credit
    path('modal_payment_credit/', login_required(get_modal_payment_credit), name='modal_payment_credit'),
    path('payment_credit/', login_required(payment_credit), name='payment_credit'),
    path('payment_list/', login_required(get_payment_list), name='payment_list'),
    # Generate PDF
    path('print_ticket_closing_cash/<int:pk>/', login_required(print_ticket_closing_cash),
         name='print_ticket_closing_cash'),
    # Detail payment
    path('payment_list/', login_required(get_payment_list), name='payment_list'),
]
