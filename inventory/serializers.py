"""
Serializers for Inventory app.
Handles Category, Product, Warehouse, and StockMovement serialization.
"""

from rest_framework import serializers
from .models import Category, Product, Warehouse, StockMovement

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializers for Category model with hierarchical support.
    """
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'parent_name', 'is_active']
        read_only_fields = ['id']

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model
    """
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'category', 'category_name', 'unit_cost', 'unit_price', 'track_stock','is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product lists
    """
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'category_name', 'unit_price', 'is_active']
        read_only_fields = ['id']

class WarehouseSerializer(serializers.ModelSerializer):
    """
    Serializer for warehouse model
    """
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location', 'is_active']
        read_only_fields = ['id']


class StockMovementSerializer(serializers.ModelSerializer):
    """
    Serializer for stock movement model
    READ ONLY - Movements created through business logic
    """

    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_sku', 'product_name', 'warehouse', 'warehouse_name', 'movement_type', 'quantity',
            'reference_type', 'reference_id', 'created_by', 'created_by_username', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class StockMovementCreate(serializers.ModelSerializer):
    """
    Serializer for creating stock movements, used by business logic
    """
    class Meta:
        model = StockMovement
        fields = [
            'product', 'warehouse', 'movement_type', 'quantity',
            'reference_type', 'reference_id', 'created_by'
        ]

    class StockLevelSerializer(serializers.Serializer):
        """
        Serializer for computed stock levels - not a model
        GET /api/stock endpoint
        """

        product_id = serializers.UUIDField()
        product_sku = serializers.CharField()
        product_name = serializers.CharField()
        warehouse_id = serializers.UUIDField()
        warehouse_name = serializers.CharField()
        current_quantity = serializers.DecimalField(max_digits=15, decimal_places=3)
        last_movement = serializers.DateTimeField(allow_null=True)