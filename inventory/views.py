"""
Views for Inventory app with role-based permissions.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Max, Q
from django.db import transaction

from .models import Category, Product, Warehouse, StockMovement
from .serializers import (
    CategorySerializer, ProductSerializer, ProductListSerializer,
    WarehouseSerializer, StockMovementSerializer, StockMovementCreateSerializer,
    StockLevelSerializer
)
from accounts.permissions import CanManageInventory, CanAdjustStock


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category management.
    ADMIN, MANAGER, STOREKEEPER can manage.
    Others can only read.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, CanManageInventory]

    def get_queryset(self):
        queryset = Category.objects.select_related('parent')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product management.
    ADMIN, MANAGER, STOREKEEPER can manage.
    Others can only read.
    """
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated, CanManageInventory]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related('category')

        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(sku__icontains=search) | Q(name__icontains=search)
            )

        return queryset


class WarehouseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Warehouse management.
    ADMIN, MANAGER can manage.
    Others can only read.
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageInventory]

    def get_queryset(self):
        queryset = Warehouse.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class StockViewSet(viewsets.ViewSet):
    """
    ViewSet for stock level queries.
    All authenticated users can view stock levels.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Get current stock levels computed from movements."""
        product_id = request.query_params.get('product_id')
        warehouse_id = request.query_params.get('warehouse_id')

        movements = StockMovement.objects.select_related(
            'product', 'warehouse'
        ).values(
            'product_id', 'product__sku', 'product__name',
            'warehouse_id', 'warehouse__name'
        )

        if product_id:
            movements = movements.filter(product_id=product_id)
        if warehouse_id:
            movements = movements.filter(warehouse_id=warehouse_id)

        stock_levels = movements.annotate(
            current_quantity=Sum('quantity'),
            last_movement=Max('created_at')
        ).filter(current_quantity__gt=0)

        serializer = StockLevelSerializer(stock_levels, many=True)
        return Response(serializer.data)


class StockMovementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StockMovement records.
    All authenticated users can view.
    Only ADMIN and STOREKEEPER can manually create adjustments.
    """
    queryset = StockMovement.objects.all()
    permission_classes = [permissions.IsAuthenticated, CanAdjustStock]
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.action == 'create':
            return StockMovementCreateSerializer
        return StockMovementSerializer

    def get_queryset(self):
        queryset = StockMovement.objects.select_related(
            'product', 'warehouse', 'created_by'
        ).order_by('-created_at')

        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        warehouse_id = self.request.query_params.get('warehouse_id')
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)

        movement_type = self.request.query_params.get('movement_type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)

        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a manual stock movement (ADJUSTMENT only)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get('movement_type') != 'ADJUSTMENT':
            return Response(
                {'error': 'Manual movements must be of type ADJUSTMENT. Other types are created automatically.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.validated_data['created_by'] = request.user
        movement = serializer.save()

        response_serializer = StockMovementSerializer(movement)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)