"""
Admin interface for Finance app.
Manages accounts and ledger entries
"""

from django.contrib import admin
from .models import Account, LedgerEntry
# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """
    Admin for chart of accounts
    """
    list_display = ['name', 'account_type', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['name']
    readonly_fields = ['id']
    ordering = ['account_type', 'name']

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    """
    Admin for Ledger Entries - READ ONLY
    Ledger entries are immutable and should only be created through business logic
    """
    list_display = ['created_at', 'account', 'amount', 'reference_type', 'reference_id']
    list_filter = ['reference_type', 'account', 'created_at']
    search_fields = ['reference_id', 'account__name']
    readonly_fields = ['id', 'account', 'amount', 'reference_type', 'reference_id', 'created_at']
    autocomplete_fields = ['account']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        """Prevents manual creation - Use business logic instead"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion - ledger entries are immutable"""
        return False