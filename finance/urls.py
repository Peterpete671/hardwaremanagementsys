"""
URL Configuration for finance App
Handles accounts and ledger entries
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, LedgerEntryViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'ledger', LedgerEntryViewSet, basename='ledger')

urlpatterns = [
    path('', include(router.urls)),
]