from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('', views.content_list, name='list'),
    path('upload/', views.upload_content, name='upload'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('bookmark/<int:content_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('like/<int:content_id>/', views.toggle_like, name='toggle_like'),
    path('bookmarks/', views.my_bookmarks, name='bookmarks'),
    path('history/', views.watch_history, name='watch_history'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('<slug:slug>/', views.content_detail, name='detail'),
]
