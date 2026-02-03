"""
Serializers for Account model
Handles account and LedgerEntry serialization
"""

from rest_framework import serializers
from .models import Account, LedgerEntry

class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for Account model
    """
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'name', 'account_type', 'is_active', 'balance']
        read_only_fields = ['id']

    def get_balance(self, obj):
        """
        calculate current account balance from ledger entries
        """
        total = sum(entry.amount for entry in obj.ledger_entries.all())
        return total

class LedgerEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for LedgerEntry model
    READ ONLY; entries should only be created through business logic
    """
    account_name = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = LedgerEntry
        fields = ['id', 'account', 'account_name', 'amount','reference_type', 'reference_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    class LedgerEntryCreateSerializer(serializers.ModelSerializer):
        """
        Serializer for creating ledger entries, used by business logic
        """
        class Meta:
            model = LedgerEntry
            fields = ['account', 'amount', 'reference_type', 'reference_id']
