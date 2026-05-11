"""
Django signals for automatic audit logging
Captures CREATE, UPDATE, DELETE operations on critical models and
stores before/after state snapshots.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
import json

from .models import AuditLog
from accounts.models import User, Role, UserRole
from inventory.models import Product, Category, Warehouse, StockMovement
from sales.models import Sale, SaleItem, Payments
from finance.models import Account, LedgerEntry

User = get_user_model()

def get_current_user():
    """
    Get current user from thread local storage
    Set by middleware
    """
    from .middleware import get_current_user as get_user
    return get_user()

def model_to_dict(instance):
    """
    Convert model instance to dictionary for JSON storage
    Handles UUIDs, Dates, and other special types.
    """
    data = {}
    for field in instance._meta.fields:
        value = getattr(instance, field.name)

        #Convert special types to JSON-serializable format
        if value is not None:
            if hasattr(value, 'isoformat'):
                data[field.name] = value.isoformat()
            elif hasattr(value, 'hex'):
                data[field.name] = str(value)
            else:
                data[field.name] = value
        else:
            data[field.name] = None

    return data

def should_audit(instance):
    """
    Determine if the model instance should be audited
    Skip audit logs themselves to prevent infinite loops.
    """
    return not isinstance(instance, AuditLog)

#Signal handlers - CREATE operations

@receiver(post_save)
def log_create(sender, instance, created, **kwargs):
    """
    Log CREATE operations for all audited models
    Fires after an object is created
    """
    if not created or not should_audit(instance):
        return

    user = get_current_user()
    if not user or not user.is_authenticated:
        return

    #Only audit specific models
    audited_models = [
        User, Role, UserRole,
        Product, Category, Warehouse, StockMovement,
        Sale, SaleItem, Payments,
        Account, LedgerEntry
    ]

    if type(instance) not in audited_models:
        return

    try:
        AuditLog.objects.create(
            user=user,
            action='CREATE',
            entity_type=sender.__name__,
            entity_id=instance.pk,
            before_state=None,
            after_state=model_to_dict(instance)
        )
    except Exception as e:
        # Don't break application if audit logging fails
        print(f"Audit logging failed: {e}")

#Signal handlers - UPDATE Operations
#Store original state before update
_pre_save_state = {}

@receiver(pre_save)
def store_pre_save_state(sender, instance, **kwargs):
    """
    Store the original state before update
    Fires before an object is saved (for updates only).
    """
    if not should_audit(instance):
        return

    #Only for existing objects (updates, not creates)

    if instance.pk:
        audited_models = [
            User, Role, UserRole,
            Product, Category, Warehouse, StockMovement,
            Sale, SaleItem, Payments,
            Account, LedgerEntry
        ]

        if type(instance) in audited_models:
            try:
                #Get the current state from database
                original = sender.objects.get(pk=instance.pk)
                _pre_save_state[f"{sender.__name__}_{instance.pk}"] = model_to_dict(original)
            except sender.DoesNotExist:
                pass

@receiver(post_save)
def log_update(sender, instance, created, **kwargs):
    """
    Log UPDATE operations for all audited models
    Fires after an object is updated.
    """
    if created or not should_audit(instance):
        return

    user = get_current_user()
    if not user or not user.is_authenticated:
        return

    audited_models = [
        User, Role, UserRole,
        Product, Category, Warehouse, StockMovement,
        Sale, SaleItem, Payments,
        Account, LedgerEntry
    ]

    if type(instance) not in audited_models:
        return

    #Get the stored before state
    state_key = f"{sender.__name__}_{instance.pk}"
    before_state = _pre_save_state.pop(state_key, None)

    if before_state is None:
        return

    try:
        AuditLog.objects.create(
            user=user,
            action='UPDATE',
            entity_type=sender.__name__,
            entity_id=instance.pk,
            before_state=before_state,
            after_state=model_to_dict(instance)
        )
    except Exception as e:
        print(f"Audit logging failed: {e}")

#Signal handlers - DELETE operation
@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """
    Log DELETE operations for all audited models
    Fires after an object is deleted.
    """
    if not should_audit(instance):
        return

    user = get_current_user()
    if not user or not user.is_authenticated:
        return

    audited_models = [
        User, Role, UserRole,
        Product, Category, Warehouse, StockMovement,
        Sale, SaleItem, Payments,
        Account, LedgerEntry
    ]

    if type(instance) not in audited_models:
        return

    try:
        AuditLog.objects.create(
            user=user,
            action='DELETE',
            entity_type=sender.__name__,
            entity_id=instance.pk,
            before_state=model_to_dict(instance),
            after_state=None
        )
    except Exception as e:
        print(f"Audit logging failed: {e}")

def log_void_action(user, entity_type, entity_id, before_state, after_state):
    """
    Manually log VOID operations
    Called from business logic when voiding
    Usage: from audit.signals import log_void_action
    log_void_action(request.user, 'Sale', sale.id, old_state, new_state)
    """
    try:
        AuditLog.objects.create(
            user=user,
            action='VOID',
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=before_state,
            after_state=after_state
        )
    except Exception as e:
        print(f"Audit logging failed: {e}")