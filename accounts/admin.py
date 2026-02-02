"""
Admin interface for Accounts app
Manages users, roles, and role assignments.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UserRole

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Extended user admin with custom fields and filters.
    """
    list_display = ['username', 'email', 'is_active', 'is_staff', 'created_at']
    list_filter = ['is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        (None, {'fields': ('id', 'username','password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates',  {'fields': ('created_at', 'updated_at', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin for business roles
    """
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at']
    ordering = ['name']

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    Admin for user-role assignments
    """
    list_display = ['user', 'role', 'is_active', 'assigned_at']
    list_filter = ['is_active', 'role', 'assigned_at']
    search_fields = ['user__username', 'role__name']
    readonly_fields = ['id', 'assigned_at']
    autocomplete_fields = ['user', 'role']
    ordering = ['-assigned_at']