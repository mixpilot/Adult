from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import UserProfile, ProfilePhoto, Connection, Message, Visit


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = [
        'user', 'gender', 'seeking', 'age', 'location',
        'body_type', 'ethnicity', 'relationship_status',
        'is_verified', 'id_verified', 'phone_verified', 'is_online',
    ]
    list_filter = [
        'gender', 'seeking', 'body_type', 'ethnicity',
        'education_level', 'relationship_status',
        'is_verified', 'id_verified', 'phone_verified', 'is_online',
    ]
    search_fields = ['user__username', 'user__email', 'location', 'bio']


@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(ModelAdmin):
    list_display = ['user', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']


@admin.register(Connection)
class ConnectionAdmin(ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    list_display = ['sender', 'recipient', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'content']


@admin.register(Visit)
class VisitAdmin(ModelAdmin):
    list_display = ['visitor', 'visited_user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['visitor__username', 'visited_user__username']
