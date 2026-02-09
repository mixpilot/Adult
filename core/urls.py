from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('premium/', views.premium_landing, name='premium'),
    path('terms/', views.terms_of_service, name='terms'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('dmca/', views.dmca_policy, name='dmca'),
    path('2257/', views.compliance_2257, name='compliance_2257'),
]
