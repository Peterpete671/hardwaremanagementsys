# audit/views.py

"""
Views for Audit app.
Handles audit log queries (read-only).
"""

from rest_framework import viewsets, permissions
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for AuditLog queries (strictly read-only).

    Endpoints:
    - GET /api/audit/
      Query params: ?entity_type=..., ?entity_id=..., ?user_id=..., ?action=...

    NOTE: Audit logs are immutable and created automatically.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter audit logs with optional query parameters.
        Supports: ?entity_type=..., ?entity_id=..., ?user_id=..., ?action=...
        """
        queryset = AuditLog.objects.select_related('user').order_by('-created_at')

        # Filter by entity type
        entity_type = self.request.query_params.get('entity_type')
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)

        # Filter by entity ID
        entity_id = self.request.query_params.get('entity_id')
        if entity_id:
            queryset = queryset.filter(entity_id=entity_id)

         # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
             queryset = queryset.filter(user_id=user_id)

        # Filter by action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset