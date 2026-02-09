from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ['username', 'email', 'user_type', 'is_verified', 'is_staff', 'date_joined']
    list_filter = ['user_type', 'is_verified', 'is_staff', 'is_superuser', 'date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('bio', 'avatar', 'date_of_birth', 'phone_number', 'user_type', 'is_verified')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number')
        }),
    )
