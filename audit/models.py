"""
AUDIT APP - Legal Protection

Purpose: Immutable audit trail for all critical operations.
Records before/after state for CREATE, UPDATE, DELETE, VOID actions.
"""
import uuid
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Comprehensive audit trail for legal compliance and debugging.

    Records the complete state before and after each operation on critical entities (User, Sale, Product, StockMovement, etc.)

    before_state and after_state store JSON snapshots of the entity.
    For CREATE: before_state is null
    For DELETE: after_state is null
    For UPDATE: both contain the full entity state

    *These records are IMMUTABLE - never update or delete.
    Use on_delete=models.PROTECT for user FK to prevent accidental deletion.
    """

    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VOID', 'Void'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='audit_logs',
        help_text="User who performed the action"
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True
    )

    entity_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Model name (e.g., Sale, Product, User)"
    )

    entity_id= models.UUIDField(
        db_index=True,
        help_text="Primary Key for affected entity"
    )

    before_state = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON snapshot before the operation"
    )

    after_state = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON snapshot after the operation"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_log'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f"{self.action} - {self.entity_type}:{self.entity_id} by {self.user.username}"