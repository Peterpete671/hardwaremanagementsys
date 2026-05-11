""""
Views for Sales app with role-based permissions.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Sum, Q
from decimal import Decimal

from .models import Sale, SaleItem, Payments
from .serializers import (
    SaleSerializer, SaleListSerializer, SaleCreateSerializer,
    SaleItemSerializer, SaleItemCreateSerializer,
    PaymentSerializer, PaymentCreateSerializer
)
from inventory.models import Product, StockMovement
from accounts.permissions import CanManageSales, IsAdminOrManager


class SaleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Sale management.
    CASHIER, MANAGER, ADMIN can create and complete sales.
    Only MANAGER and ADMIN can void and refund.
    """
    queryset = Sale.objects.all()
    permission_classes = [permissions.IsAuthenticated, CanManageSales]

    def get_serializer_class(self):
        if self.action == 'list':
            return SaleListSerializer
        elif self.action == 'create':
            return SaleCreateSerializer
        return SaleSerializer

    def get_queryset(self):
        queryset = Sale.objects.select_related('warehouse', 'sold_by')

        sale_status = self.request.query_params.get('status')
        if sale_status:
            queryset = queryset.filter(status=sale_status)

        warehouse_id = self.request.query_params.get('warehouse_id')
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset.order_by('-created_at')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a draft sale."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Generate sale number
        last_sale = Sale.objects.order_by('-created_at').first()
        if last_sale and last_sale.sale_number:
            try:
                last_number = int(last_sale.sale_number.split('-')[-1])
                sale_number = f"SALE-{last_number + 1:06d}"
            except:
                sale_number = f"SALE-000001"
        else:
            sale_number = f"SALE-000001"

        sale = serializer.save(
            sale_number=sale_number,
            status='PENDING',
            sold_by=request.user
        )

        response_serializer = SaleSerializer(sale)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        """Add an item to the sale."""
        sale = self.get_object()

        if sale.status != 'PENDING':
            return Response(
                {'error': 'Can only add items to pending sales'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SaleItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        sale_item = SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            unit_price=product.unit_price,
            line_total=product.unit_price * quantity
        )

        self._recalculate_sale_totals(sale)

        response_serializer = SaleItemSerializer(sale_item)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        """Remove an item from the sale."""
        sale = self.get_object()

        if sale.status != 'PENDING':
            return Response(
                {'error': 'Can only remove items from pending sales'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sale_item = SaleItem.objects.get(id=item_id, sale=sale)
        except SaleItem.DoesNotExist:
            return Response(
                {'error': 'Sale item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        sale_item.delete()
        self._recalculate_sale_totals(sale)

        return Response({'message': 'Item removed successfully'})

    @action(detail=True, methods=['post'], url_path='payments')
    def add_payment(self, request, pk=None):
        """Add a payment to the sale."""
        sale = self.get_object()

        if sale.status not in ['PENDING', 'COMPLETED']:
            return Response(
                {'error': 'Cannot add payment to voided or refunded sales'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = Payments.objects.create(
            sale=sale,
            **serializer.validated_data
        )

        response_serializer = PaymentSerializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def complete(self, request, pk=None):
        """Complete a sale: validate stock, reduce inventory."""
        sale = self.get_object()

        if sale.status != 'PENDING':
            return Response(
                {'error': 'Only pending sales can be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not sale.items.exists():
            return Response(
                {'error': 'Sale must have at least one item'},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_paid = sale.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        if total_paid < sale.grand_total:
            return Response(
                {'error': f'Insufficient payment. Paid: {total_paid}, Required: {sale.grand_total}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate stock availability
        for item in sale.items.select_related('product'):
            if item.product.track_stock:
                current_stock = StockMovement.objects.filter(
                    product=item.product,
                    warehouse=sale.warehouse
                ).aggregate(total=Sum('quantity'))['total'] or Decimal('0')

                if current_stock < item.quantity:
                    return Response(
                        {'error': f'Insufficient stock for {item.product.sku}. Available: {current_stock}, Required: {item.quantity}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # Create stock movements
        for item in sale.items.select_related('product'):
            if item.product.track_stock:
                StockMovement.objects.create(
                    product=item.product,
                    warehouse=sale.warehouse,
                    movement_type='SALE',
                    quantity=-item.quantity,
                    reference_type='SALE',
                    reference_id=sale.id,
                    created_by=request.user
                )

        sale.status = 'COMPLETED'
        sale.save()

        serializer = SaleSerializer(sale)
        return Response({
            'message': 'Sale completed successfully',
            'sale': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminOrManager])
    @transaction.atomic
    def void(self, request, pk=None):
        """Void a pending sale. Only MANAGER/ADMIN can void."""
        sale = self.get_object()

        if sale.status != 'PENDING':
            return Response(
                {'error': 'Only pending sales can be voided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sale.status = 'VOIDED'
        sale.save()

        return Response({'message': 'Sale voided successfully'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminOrManager])
    @transaction.atomic
    def refund(self, request, pk=None):
        """Refund a completed sale. Only MANAGER/ADMIN can refund."""
        sale = self.get_object()

        if sale.status != 'COMPLETED':
            return Response(
                {'error': 'Only completed sales can be refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create reversing stock movements
        for item in sale.items.select_related('product'):
            if item.product.track_stock:
                StockMovement.objects.create(
                    product=item.product,
                    warehouse=sale.warehouse,
                    movement_type='REFUND',
                    quantity=item.quantity,
                    reference_type='SALE',
                    reference_id=sale.id,
                    created_by=request.user
                )

        sale.status = 'REFUNDED'
        sale.save()

        return Response({'message': 'Sale refunded successfully'})

    def _recalculate_sale_totals(self, sale):
        """Helper method to recalculate sale totals from items."""
        subtotal = sale.items.aggregate(total=Sum('line_total'))['total'] or Decimal('0')
        sale.subtotal = subtotal
        sale.discount_total = Decimal('0')
        sale.tax_total = Decimal('0')
        sale.grand_total = subtotal - sale.discount_total + sale.tax_total
        sale.save()
