"""
ACCOUNTS APP - Identity, roles and permissions
Purpose: Manages user authentication and business role assignments.
NB: Business roles are separate from Django's permission system.
"""

from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Extended Django user model for authentication and identity.
    Used UUID as PK for security and distributed system compatibility.
    Tracks active status ad timestamps for audit purposes.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

class Role(models.Model):
    """
    Business roles for the system (e.g. ADMIN, MANAGER, CASHIER)
    Not Django groups or permissions, they represent business-level access control separate in Django's built-in permission system.

    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Role name (e.g. ADMIN, MANAGER, CASHIER, STOREKEEPER)"
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role'
        verbose_name = 'Role'
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name

class UserRole(models.Model):
    """
    Assignment of business roles to users
    Allows users to have multiple roles that can be activated or deactivated without deletion.
    Tracks when each role was assigned for audit purposes
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_role'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        unique_together = [['user', 'role']]

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"