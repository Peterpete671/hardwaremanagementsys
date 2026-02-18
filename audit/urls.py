"""
URL configuration for Audit app
Handles audit log queries
Strictly read only
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet

router = DefaultRouter()
router.register(r'accounts', AuditLogViewSet, basename='audit')

urlpatterns = [
    path('', include(router.urls)),
]