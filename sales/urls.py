"""
URL configuration for sales app
Handles sales, items, payments, and sale workflows
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet

router = DefaultRouter()
router.register(r'sales', SaleViewSet, basename='sale')

urlpatterns = [
    path('', include(router.urls)),
]