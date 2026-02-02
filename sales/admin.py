"""
Admin interface for Sales App
Manages sales, sale items and payments
"""
from django.contrib import admin
from .models import Sale, SaleItem, Payments

class SaleItemInline(admin.TabularInline):
    """
    Inline Admin for sale items within a sale.
    """

    model = SaleItem
    extra = 0
    readonly_fields = ['id', 'product', 'quantity', 'unit_price', 'line_total']
    autocomplete_fields = ['product']

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of completed sale items."""
        if obj and obj.sale.status == 'COMPLETED':
            return False
        return True
    

class PaymentInline(admin.TabularInline):
    """
    Inline admin for payments within a sale
    """
    model = Payments
    extra = 0
    readonly_fields = ['id', 'payment_method', 'amount', 'reference_code', 'received_by', 'created_at']
    autocomplete_fields = ['received_by']

    def has_delete_permission(self, request, obj=None):
        """Prevents deletion of payments"""
        return False
    
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """
    Admin for sales with inline items and payments.
    """
    list_display = ['sale_number', 'warehouse', 'sold_by', 'status', 'grand_total', 'created_at']
    list_filter = ['status', 'warehouse', 'created_at']
    search_fields = ['sale_number', 'sold_by__username']
    readonly_fields = ['id', 'sale_number', 'created_at']
    autocomplete_fields = ['warehouse', 'sold_by']
    ordering = ['-created_at']
    inlines = [SaleItemInline, PaymentInline]

    fieldsets = (
        ('Sale Information', {
            'fields': ('id', 'sale_number', 'warehouse', 'sold_by', 'status', 'created_at')
        }),
        ('Totals', {
            'fields': ('subtotal', 'discount_total', 'tax_total', 'grand_total')
        }),
    )


    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of completed sales"""
        if obj and obj.status in ['COMPLETED', 'REFUNDED']:
            return False
        return True
    
@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    """ 
    Standalone admin for sale items (Usually accessed via Sale Inline).
    """
    list_display = ['sale', 'product', 'quantity', 'unit_price', 'line_total']
    list_filter = ['sale__status', 'sale__created_at']
    search_fields = ['sale__sale_number', 'product__sku', 'product_name']
    readonly_fields = ['id', 'sale', 'product', 'quantity', 'unit_price', 'line_total']
    autocomplete_fields = ['sale', 'product']
    ordering = ['-sale__created_at']

    def has_add_permission(self, request):
        """Items should be added through the Sale admin."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of complete sale items"""
        if obj and obj.sale.status == 'COMPLETED':
            return False
        return True

@admin.register(Payments)
class PaymentAdmin(admin.ModelAdmin):
    """
    Standalone admin for payments (Usually accessed via Sale)
    """
    list_display = ['sale', 'payment_method', 'amount', 'reference_code', 'received_by', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['sale__sale_number', 'reference_code', 'received_by__username']
    readonly_fields = ['id', 'sale', 'payment_method', 'amount', 'reference_code', 'received_by', 'created_at']
    autocomplete_fields = ['sale', 'received_by']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        """Payments should be added through Sale admin or API"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion - payments are immutable"""
        return False