from django.urls import path
from . import views

app_name = 'connections'

urlpatterns = [
    path('browse/', views.browse_users, name='browse'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('connect/<int:user_id>/', views.connect_user, name='connect'),
    path('block/<int:user_id>/', views.block_user, name='block'),
    path('connections/', views.connections_list, name='connections_list'),
    path('messages/', views.messages_list, name='messages_list'),
    path('chat/<int:user_id>/', views.chat, name='chat'),
    path('upload-photo/', views.upload_photo, name='upload_photo'),
]
