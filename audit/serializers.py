"""
Serializers for Audit app
Handles AuditLog serialization
"""

from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_username', 'action',
            'entity_type', 'before_state', 'after_state', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'action', 'entity_type', 'entity_id', 'before_state', 'after_state', 'created_at']

class AuditLogCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating audit logs
    Used by signals/business logic
    """
    class Meta:
        model = AuditLog
        fields = ['user', 'action', 'entity_type', 'entity_id', 'before_state', 'after_state']