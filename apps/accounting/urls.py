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
    # Generate PDF
    path('print_ticket_closing_cash/<int:pk>/', login_required(print_ticket_closing_cash),
         name='print_ticket_closing_cash'),

]
