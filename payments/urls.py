from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('mpesa/status/<int:payment_id>/', views.mpesa_status, name='mpesa_status'),
]
