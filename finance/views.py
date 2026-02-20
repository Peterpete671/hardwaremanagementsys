"""
Views for Finance app with role-based permissions.
"""

from rest_framework import viewsets, permissions
from .models import Account, LedgerEntry
from .serializers import AccountSerializer, LedgerEntrySerializer
from accounts.permissions import CanViewFinance


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Account management.
    Only ADMIN and MANAGER can view.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewFinance]

    def get_queryset(self):
        queryset = Account.objects.all()

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        account_type = self.request.query_params.get('account_type')
        if account_type:
            queryset = queryset.filter(account_type=account_type)

        return queryset


class LedgerEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for LedgerEntry queries.
    Only ADMIN and MANAGER can view.
    """
    queryset = LedgerEntry.objects.all()
    serializer_class = LedgerEntrySerializer
    permission_classes = [permissions.IsAuthenticated, CanViewFinance]

    def get_queryset(self):
        queryset = LedgerEntry.objects.select_related('account').order_by('-created_at')

        account_id = self.request.query_params.get('account_id')
        if account_id:
            queryset = queryset.filter(account_id=account_id)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        reference_type = self.request.query_params.get('reference_type')
        if reference_type:
            queryset = queryset.filter(reference_type=reference_type)

        return queryset