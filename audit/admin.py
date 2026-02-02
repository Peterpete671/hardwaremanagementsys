"""
Admin interface for Audit app
Manages audit logs (read-only)
"""
from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin for Audit logs - STRICTLY READ ONLY
    Audit logs are immutable legal records and must never be modified or deleted.
    """
    list_display = ['created_at', 'user', 'action', 'entity_type', 'entity_id']
    list_filter = ['action', 'entity_type', 'created_at']
    search_fields = ['entity_id', 'user__username', 'entity_type']
    readonly_fields = ['id', 'user', 'action', 'entity_type', 'entity_id', 'before_state', 'after_state', 'created_at']
    autocomplete_fields = ['user']
    ordering = ['-created_at']

    fieldsets = (
        ('Audit Information', {
            'fields': ('before_state', 'after_state'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Prevent manual creation - use signals or business logic"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion - audit logs are immutable"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing - audit logs are immutable"""
        return False