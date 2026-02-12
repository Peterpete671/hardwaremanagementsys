"""
Views for inventory app
Handles categories, products, warehouses, and stock.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Max, Q
from django.db import transaction

from .models import Category, Product, Warehouse, StockMovement
from .serializers import (
    CategorySerializer, ProductSerializer, ProductListSerializer,
    WarehouseSerializer, StockMovementSerializer, StockMovementCreateSerializer, StockLevelSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for category management
    -GET /api/categories/
    -POST /api/categories/
    -GET /api/categories/{id}/
    -PUT/PATCH /api/categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter active categories by default"""
        queryset = Category.objects.select_related('parent')

        #Optional filter for active/inactive
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product management.
    -GET /api/products/
    -POST /api/products/
    -GET /api/products/{id}/
    -PUT/PATCH /api/products/{id}/
    """

    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Filter products with optional query parameters
        Supports: ?category_id?is_active=..., ?search=...
        """
        queryset = Product.objects.select_related('category')

        #Filter by category
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        #filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        #Search by SKU or name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(sku__icontains=search) | Q(name__icontains=search)
            )
        return queryset

class WarehouseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Warehouse Management
    -GET /api/warehouses/
    -POST /api/warehouses/
    -GET /api/warehouses/{id}/
    """

    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter active warehouses by default"""
        queryset = Warehouse.objects.all()

        is_active = self.request.query.params_get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

class StockViewSet(viewsets.ViewSet):
    """
    ViewSet for stock level queries
    Computed from movements
    -GET /api/stock/
    Query params: ?product_id=..., ?warehouse_id=...

    STOCK LEVELS ARE COMPUTED, NOT STORED
    """

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Get current stock levels computed from movements
        GET /api/stock/
        """

        product_id = request.query.params_get('product_id')
        warehouse_id = request.query.params.get('warehouse_id')

        #Build base query
        movements = StockMovement.objects.select_related(
            'product', 'warehouse'
        ).values(
            'product_id', 'product__sku', 'product__name',
            'warehouse_id', 'warehouse__name'
        )

        #Apply filters
        if product_id:
            movements = movements.filter(product_id=product_id)
        if warehouse_id:
            movements = movements.filter(warehouse_id=warehouse_id)

        #Compute stock levels
        stock_levels = movements.annotate(
            current_quantity=Sum('quantity'),
            last_movement=Max('created_at')
        ).filter(
            current_quantity__gt=0
        )

        #Serialize results
        serializer = StockLevelSerializer(stock_levels, many=True)
        return Response(serializer.data)

class StockMovementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StockMovement records.

    Endpoints:
    -GET /api/stock/movements/ (read-only, for audit)
    -POST /api/stock/movements/ (create manual adjustments)

    Most movements are created automatically for business logic
    Manual creation should be restricted to ADJUSTMENT type only
    """

    queryset = StockMovement.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        """Use different serializers for read/write."""
        if self.action == 'create':
            return StockMovementCreateSerializer
        return StockMovementSerializer

    def get_queryset(self):
        """
        Filter movements with optional query parameters
        """
        queryset = StockMovement.objects.select_related(
            'product', 'warehouse', 'created_by'
        ).order_by('-created_at')

        #Filter by product
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        #Filter by warehouse
        warehouse_id = self.request.query_params.get('warehouse_id')
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)

        #Filter by movement type
        movement_type = self.request.query_params.get('movement_type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)

        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create manual stock movement (Adjustment Only)

        POST /api/stock/movements/
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        #Restrict manual creation to adjustment type
        if serializer.validated_data.get('movement_type') != 'ADJUSTMENT':
            return Response(
                {'error': 'Manual movements must be of type ADJUSTMENT. Other types are created automatically'},
                status = status.HTTP_400_BAD_REQUEST
            )

        #Set created_by to current user
        serializer.validated_data['created_by'] = request.user

        movement = serializer.save()

        response_serializer = StockMovementSerializer(movement)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)