"""
Admin interface for inventory app.
Manages credentials, products, warehouses, and stock movements.
"""
from django.contrib import admin
from .models import Category, Product, Warehouse, StockMovement

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin for product categories with hierarchical support.
    """
    list_display = ['name', 'parent', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    readonly_fields = ['id']
    autocomplete_fields = ['parent']
    ordering = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin for products with cost/price tracking.

    """
    list_display = ['sku', 'name', 'category', 'unit_cost', 'unit_price', 'track_stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'track_stock', 'category', 'created_at']
    search_fields = ['sku', 'name']
    readonly_fields = ['id','created_at']
    autocomplete_fields = ['category']
    ordering = ['sku']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'sku', 'name', 'category')
        }),
        ('Pricing', {
            'fields': ('unit_cost','unit_price')
        }),
        ('Settings', {
            'fields': ('track_stock', 'is_active', 'created_at')
        }),
    )

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    """
    Admin for warehouse locations.
    """
    list_display = ['name', 'location', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'location']
    readonly_fields = ['id']
    ordering = ['name']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """
    Admin for stock movements - READ ONLY for safety
    Stock Movements should only be created through business logic
    """

    list_display = ['created_at', 'product', 'warehouse', 'movement_type', 'quantity', 'reference_type','reference_id', 'created_by', 'created_at']
    list_filter = ['movement_type', 'reference_type', 'warehouse', 'created_at']
    search_fields = ['product__sku', 'product__name', 'reference_id']
    readonly_fields = ['id', 'product', 'warehouse', 'movement_type', 'quantity', 'reference_type', 'reference_id', 'created_by', 'created_at']
    autocomplete_fields = ['product', 'warehouse', 'created_by']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        """Prevent manual creation - Business Logic Instead"""
        return False

    def has_delete_permission(self, request, obj =None):
        """Prevent deletion - movements are immutable"""
        return False