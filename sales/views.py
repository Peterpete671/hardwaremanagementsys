"""
Views for Sales app
Handles sales, sale items, payments, and sale competition workflow
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from decimal import Decimal

from .models import Sale, SaleItem, Payments
from .serializers import  (
    SaleSerializer, SaleListSerializer, SaleCreateSerializer, SaleItemSerializer,
    SaleItemCreateSerializer, PaymentSerializer, PaymentCreateSerializer
)
from inventory.models import Product, StockMovement

class SaleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for sale sale management

    -GET /api/sales/
    -POST /api/sales/ (Create draft)
    -GET /api/sales/{id}/
    -POST /api/sales/{id}/items/
    -DELETE /api/sales/{id}/items/{item_id}/
    -POST /api/sales/{id}/payments/
    -POST /api/sales/{id}/complete/
    -POST /api/sales/{id}/void/
    -POST /api/sales/{id}/refund/
    """

    queryset = Sale.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """ Use different serializer for different actions."""
        if self.action == 'list':
            return SaleListSerializer
        elif self.action == 'create':
            return SaleCreateSerializer
        return SaleSerializer

    def get_queryset(self):
        """
        Filter sales with optional query parameters
        """
        queryset = Sale.objects.select_related('warehouse', 'sold_by')

        #Filter by status
        sale_status = self.request.query_params.get('status')
        if sale_status:
            queryset = queryset.filter(status=sale_status)

        #Filter by warehouse
        warehouse_id = self.request.query_params.get('warehouse_id')
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)

        #Filter by data range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        return  queryset.order_by('-created_at')

    @transaction.atomic
    def create(self, request, args, **kwargs):
        """
        Create a draft sale.
        POST /api/sales/
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        #Generate sale number
        last_sale = Sale.objects.order_by('-created_at').first()
        if last_sale and last_sale.sale_number:
            try:
                last_number = int(last_sale.sale_number.split('-')[1])
                sale_number = f"SALE-{last_number + 1:06d}"
            except:
                sale_number = f"SALE-000001"
        else:
            sale_number = f"SALE-000001"

        sale = serializer.save(
            sale_number=sale_number,
            status='PENDING'
        )

        response_serializer = SaleSerializer(sale)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        """
        Add an item to the sale
        POST /api/sales/{id}/items/
        """
        sale = self.get_object()

        if sale.status != 'PENDING':
            return Response(
                {'error': 'Can only add items to pending sales'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SaleItemCreateSerializer(data=request.data)
        quantity = serializer.validated_data.get('quantity')

        #Create sale item with current product price
        sale_item = SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            unit_price=product.unit_price,
            line_total=product.unit_price * quantity
        )

        #Recalculate sale totals
        self._recalculate_sale_totals(sale)

        response_serializer = SaleItemSerializer(sale_item)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        """
        Remove an item from a sale
        DELETE /api/sales/{id}/items/{item_id}/
        """

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
                {'error': 'sale item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        sale_item.delete()

        #Recalculate sale totals
        self._recalculate_sale_totals(sale)

        return Response({'message': 'Item removed successfully'})

    @action(detail=True, methods=['post'], url_path='payments')
    def add_payment(self, request, pk=None):
        """
        Add a payment to a sale
        POST /api/sales/{id}/payments/
        """
        sale = self.get_object()

        if sale.status not in ['PENDING', 'COMPLETED']:
            return Response(
                {'error': 'Cannot add payment to voided or refunded sales'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create payment
        payment = Payment.objects.create(
            sale=sale,
            **serializer.validated_data
        )

        response_serializer = PaymentSerializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def complete(self, request, pk=None):
        """
        Complete a sale: validate stock, reduce inventory, create ledger entries.

        POST /api/sales/{id}/complete/
        """
        sale = self.get_object()

        if sale.status != 'PENDING':
            return Response(
                {'error': 'Only pending sales can be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate sale has items
        if not sale.items.exists():
            return Response(
                {'error': 'Sale must have at least one item'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate payment
        total_paid = sale.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        if total_paid < sale.grand_total:
            return Response(
                {'error': f'Insufficient payment. Paid: {total_paid}, Required: {sale.grand_total}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate stock availability
        for item in sale.items.select_related('product'):
            if item.product.track_stock:
                # Calculate current stock
                current_stock = StockMovement.objects.filter(
                    product=item.product,
                    warehouse=sale.warehouse
                ).aggregate(total=Sum('quantity'))['total'] or Decimal('0')

                if current_stock < item.quantity:
                    return Response(
                        {
                            'error': f'Insufficient stock for {item.product.sku}. Available: {current_stock}, Required: {item.quantity}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # Create stock movements
        for item in sale.items.select_related('product'):
            if item.product.track_stock:
                StockMovement.objects.create(
                    product=item.product,
                    warehouse=sale.warehouse,
                    movement_type='SALE',
                    quantity=-item.quantity,  # Negative for reduction
                    reference_type='SALE',
                    reference_id=sale.id,
                    created_by=request.user
                )

        # Update sale status
        sale.status = 'COMPLETED'
        sale.save()

        # TODO: Create ledger entries (will be implemented in finance service)

        serializer = SaleSerializer(sale)
        return Response({
            'message': 'Sale completed successfully',
            'sale': serializer.data
        })

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def void(self, request, pk=None):
        """
        Void a pending sale.

        POST /api/sales/{id}/void/
        """
        sale = self.get_object()

        if sale.status != 'PENDING':
            return Response(
                {'error': 'Only pending sales can be voided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sale.status = 'VOIDED'
        sale.save()

        return Response({'message': 'Sale voided successfully'})

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def refund(self, request, pk=None):
        """
        Refund a completed sale: restore stock, create reversing ledger entries.

        POST /api/sales/{id}/refund/
        """
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
                    quantity=item.quantity,  # Positive to restore stock
                    reference_type='SALE',
                    reference_id=sale.id,
                    created_by=request.user
                )

        # Update sale status
        sale.status = 'REFUNDED'
        sale.save()

        # TODO: Create reversing ledger entries

        return Response({'message': 'Sale refunded successfully'})

    def _recalculate_sale_totals(self, sale):
        """Helper method to recalculate sale totals from items."""
        subtotal = sale.items.aggregate(total=Sum('line_total'))['total'] or Decimal('0')

        sale.subtotal = subtotal
        sale.discount_total = Decimal('0')  # TODO: Implement discount logic
        sale.tax_total = Decimal('0')  # TODO: Implement tax logic
        sale.grand_total = subtotal - sale.discount_total + sale.tax_total
        sale.save()
