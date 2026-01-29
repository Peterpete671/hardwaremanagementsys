"""
INVENTORY APP - PHYSICAL TRUTH OF STOCK
Purpose: Manage products, warehouses, and stock movements.
Key principle: Stock quantity is never stored, It is computed from movements.
"""
import uuid
from django.db import models
from django.conf import settings

class Category(models.Model):
    """
    Product categorization with hierarchical support
    Self-referential relationship allows nested categories
    (E.g. Electronics > Cables > HDMI Cables)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=150, db_index=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Product master record.

    track_stock = False allows for services, cables sold as bundles, or items that don't require inventory tracking.
    Unit cost and price are stored here but copied to sale items to preserve history.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Stock Keeping Unit - Unique Product Identifier"
    )
    name = models.CharField(max_length=255, db_index=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Cost price per unit"
    )
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Selling price per unit"
    )
    track_stock = models.BooleanField(
        default=True,
        help_text="False for services or non-tracked items"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'product'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"{self.sku} - {self.name}"

class Warehouse(models.Model):
    """
    Physical storage locations for inventory
    Each warehouse maintains separate stock levels computed from movements specific to that location
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=200, unique=True, db_index=True)
    location = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'warehouse'
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'

        def __str__(self):
            return self.verbose_name

class StockMovement(models.Model):
    """
    The heart of the inventory system, every stock exchange is recorded here.
    There is NO current_quantity field anywhere in the system.
    Stock levels are computed as SUM(quantity) grouped by product and warehouse.

    Movement Types:
    -IN: Stock received (purchase, production)
    -OUT: Stock removed (damaged, lost)
    -ADJUSTMENT: Manual correction
    -TRANSFER_IN: Received from another warehouse
    -TRANSFER_OUT: Sent to another warehouse
    -REFUND: Returned by customer

    Quantity is signed: positive for increases, negative for decreases.
    Reference fields link to source transitions (Sale, Purchase, etc.)
    """
    MOVEMENT_TYPE_CHOICES = [
        ('IN', 'In'),
        ('OUT', 'Out'),
        ('ADJUSTMENT', 'Adjustment'),
        ('TRANSFER_IN', 'Transfer In'),
        ('TRANSFER_OUT', 'Transfer Out'),
        ('SALE', 'Sale'),
        ('REFUND', 'Refund'),
    ]

    REFERENCE_TYPE_CHOICES = [
        ('SALE', 'Sale'),
        ('PURCHASE', 'Purchase'),
        ('MANUAL', 'Manual'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='movements'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='movements'
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES,
        db_index = True
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        help_text="Signed quantity: positive for IN, negative for OUT"
    )

    reference_type = models.CharField(
        max_length=20,
        choices=REFERENCE_TYPE_CHOICES
    )

    reference_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Links to sale, purchase, or other source transaction"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='stock_movements'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'stock_movement'
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['reference_type', 'reference_id']),
            models.Index(fields=['created_by', 'created_at']),
        ]

    def __str__(self):
        return f"{self.movement_type} - {self.product.sku} - {self.quantity}"