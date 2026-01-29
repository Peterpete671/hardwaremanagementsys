"""
SALES APP - Selling without Lying to Inventory or Finance
Purpose: Manage sales transactions, line items, and payments.
KEY PRINCIPLE: Prices are copied at sale time to preserve history
"""

from django.db import models
import uuid
from django.conf import settings
from inventory.models import Product, Warehouse

# Create your models here.
class Sale(models.Model):
    """
    Sales transaction header

    Status workflow:
    -PENDING: Draft sle, items being added
    -COMPLETED: Finalized, stock reduced, ledger entries created
    -VOIDED: Canceled before completion
    -REFUNDED: Completed but later refunded

    Totals are denormalized for performance but can be recalculated from line items for verification
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('VOIDED', 'Voided'),
        ('REFUNDED', 'Refunded'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    sale_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Human-readable sale reference e.g. SALE-2026-001"
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='sales'
    )

    sold_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sales'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )

    subtotal = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    tax_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    discount_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0

    )

    grand_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'sale'
        verbose_name = 'Sale'
        verbose_name_plural = "Sales"

    def __str__(self):
        return self.sale_number

class SaleItem(models.Model):
    """
    Individual line items in a sale
    CRITICAL: Unit_price is copied on purpose. Product prices change over time, but historical sales must reflect the price at the time of sale.
    Never reference Product.unit_price directly for reporting.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    sale = models.ForeignKey(
        Sale,
        on_delete=models.PROTECT,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='sale_items'
    )

    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
    )

    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        help_text="Price at time of sale copied from Product"
    )

    line_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="quantity * unit_price"
    )

    class Meta:
        db_table = 'sale_item'
        verbose_name = 'Sale Item'
        verbose_name_plural = "Sale Items"

    def __str__(self):
        return f"{self.sale.sale_number} - {self.product.sku}"

class Payments(models.Model):
    """
    Payments records for sales.
    A sale can have multiple payments (split payment methods - installments)
    Reference code stores transaction IDs from payment providers
    (M-Pesa code, card authorization, etc).
    """
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('MPESA', 'M-Pesa'),
        ('CARD', 'Card'),
        ('BANK', 'Bank Transfer'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    sale = models.ForeignKey(
        Sale,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        db_index=True
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    reference_code = models.CharField(
        max_length=200,
        unique=True,
        blank=True,
        help_text="External transaction reference e.g. M-Pesa code, etc."
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments_received'
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'payment'
        verbose_name = 'Payment'
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"{self.sale.sale_number} - {self.payment_method} - {self.amount}"