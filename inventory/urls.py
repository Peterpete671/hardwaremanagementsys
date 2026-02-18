"""
URL configuration fot Inventory app
Handles category, products, warehouses, and stock
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ProductViewSet, WarehouseViewSet,
    StockViewSet, StockMovementViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'stocks', StockMovementViewSet, basename='stock-movement')

urlpatterns = [
    path('stock/', StockViewSet.as_view({'get': 'list'}), name='stock-levels'),
    path('', include(router.urls)),
]