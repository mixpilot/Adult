from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # Subscription plans
    path('plans/', views.subscription_plans, name='plans'),
    path('review/', views.review_subscription, name='review_subscription'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('payment/<int:payment_id>/', views.payment_instructions, name='payment_instructions'),
    path('payment/<int:payment_id>/till/', views.till_payment, name='till_payment'),
    path('payment/<int:payment_id>/mpesa-waiting/', views.mpesa_waiting, name='mpesa_waiting'),
    path('payment/<int:payment_id>/confirm/', views.confirm_payment, name='confirm_payment'),
    path('success/', views.subscription_success, name='success'),
    path('cancel/', views.cancel_subscription, name='cancel'),
    path('manage/', views.manage_subscription, name='manage'),
    
    # Webhooks (optional, for future Stripe integration)
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    # Tokens
    path('tokens/', views.token_balance, name='tokens'),
    path('tokens/purchase/', views.purchase_tokens, name='purchase_tokens'),
    path('tokens/history/', views.token_history, name='token_history'),
    
    # Tips
    path('tip/<int:user_id>/', views.tip_creator, name='tip_creator'),
    
    # Creator earnings
    path('earnings/', views.creator_earnings, name='creator_earnings'),
    
    # Pay-per-view
    path('ppv/<slug:content_slug>/', views.purchase_ppv, name='purchase_ppv'),
]
