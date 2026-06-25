from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('mpesa/status/<int:payment_id>/', views.mpesa_status, name='mpesa_status'),
    path('c2b/validation/', views.c2b_validation, name='c2b_validation'),
    path('c2b/confirmation/', views.c2b_confirmation, name='c2b_confirmation'),
]
