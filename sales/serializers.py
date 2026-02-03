"""
Serializers for sales app
Handles Sale, SaleItem, and Payment Serialization
"""

from rest_framework import serializers
from .models import Sale, SaleItem, Payments
from inventory.serializers import ProductListSerializer

class SaleItemSerializer(serializers.ModelSerializer):
    """
    Serializer for SaleItem model
    """
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SaleItem
        fields = ['id', 'sale', 'product', 'product_sku', 'product_name', 'quantity', 'unit_price', 'line_total']
        read_only_fields = ['id', 'line_total']

class SaleItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating sale items
    Unit price and line total are computed automatically.
    """

    class Meta:
        model = SaleItem
        fields = ['product', 'quantity']

        def validate_quantity(self, value):
            """Ensure quantity is positive"""
            if value <=0:
                raise serializers.ValidationError("Qty must be greater than 0")
            return value


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializers for payment model
    """
    received_by_username = serializers.CharField(source='received_by.username', read_only=True)

    class Meta:
        model = Payments
        fields = ['id', 'sale', 'payment_method', 'amount', 'reference_code', 'received_by', 'received_by_username', 'created_at']
        read_only_fields = ['id', 'created_at']

class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating payments
    """
    class Meta:
        model = Payments
        fields = ['payment_method', 'amount', 'reference_code', 'received_by']

    def validate_amount(self, value):
        """Ensure amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value

class SaleSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for sale model with nested items and payments.
    """
    warehouse_name = serializers.CharField(source='warehouse.name', read_only =True)
    sold_by_username = serializers.CharField(source='sold_by_username', read_only=True)
    items = SaleItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    total_paid = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = [
            'id', 'sale_number', 'warehouse', 'warehouse_name', 'sold_by', 'sold_by_username',
            'status', 'subtotal', 'discount_total', 'tax_total', 'grand_total', 'items', 'payments',
            'total_paid', 'balance_due', 'created_at'
        ]
        read_only_fields = ['id', 'sale_number', 'created_at']

    def get_total_paid(self, obj):
        """Calculate total amount paid"""
        return sum(payment.amount for payment in obj.payments.all())

    def get_balance_due(self, obj):
         """Calculate remaining balance"""
         total_paid = self.get_total_paid(obj)
         return obj.grand_total - total_paid

class SaleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for sales lists
    """
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    sold_by_username = serializers.CharField(source='sold_by.username', read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'sale_number', 'warehouse_name', 'sold_by_username',
            'status', 'grand_total', 'created_at'
        ]
        read_only_fields = ['id', 'sale_number', 'created_at']

class SaleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating draft sales
    """
    class Meta:
        model = Sale
        fields = ['warehouse', 'sold_by']




