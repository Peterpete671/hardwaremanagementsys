"""
Custom permissions classes for role-based access control
"""

from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission classes to check if user has Admin role
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always have admin access
        if request.user.is_superuser:
            return True

        #Check if user has ADMIN role
        return request.user.user_roles.filter(
            role__name='ADMIN',
            is_active=True
        ).exists()

class IsAdminOrManager(permissions.BasePermission):
    """
    Permission class to check if user has ADMIN or MANAGER role
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True
        #Check if user has ADMIN or MANAGER role
        return request.user.user_roles.filter(
            role__name__in=['ADMIN', 'MANAGER'],
            is_active=True
        ).exists()

class IsStorekeeper(permissions.BasePermission):
    """
    Permission class to check if the user has STOREKEEPER role
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        #Check if user has STOREKEEPER or ADMIN role

        return request.user.user_roles.filter(
            role__name__in=['STOREKEEPER', 'ADMIN'],
            is_active=True
        ).exists()

class IsCashier(permissions.BasePermission):
    """
    Permissions class to check if the user has Cashier role
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        #Check if user has CASHIER, MANAGER or ADMIN role
        return request.user.user_roles.filter(
            role__name__in=['CASHIER', 'MANAGER', 'ADMIN'],
            is_active=True
        ).exists()
class CanManageUsers(permissions.BasePermission):
    """
    Permission for user management operations
    Only ADMIN can create, update, or delete users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
             return False

        if request.method in permissions.SAFE_METHODS:
              return True

         #Write operations for ADMIN only
        if request.user.is_superuser:
             return True

        return request.user.user_roles.filter(
            role__name='ADMIN',
            is_active=True
        ).exists()

class CanManageInventory(permissions.BasePermission):
    """
    Permission for inventory management
    ADMIN, MANAGER, and STOREKEEPER can manage inventory.
    Others can only read
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        #Read operations allowed for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        #Write operations for ADMIN, MANAGER, STOREKEEPER
        if request.user.is_superuser:
            return True

        return request.user.user_roles.filter(
            role__name__in=['ADMIN', 'MANAGER', 'STOREKEEPER'],
            is_active=True
        ).exists()

class CanAdjustStock(permissions.BasePermission):
    """
    Permission for manual stock adjustments
    Only ADMIN and STOREKEEPER can manually adjust stock
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        #Read operations allowed for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        #Manual adjustments only for ADMIN and STOREKEEPER
        if request.user.is_superuser:
            return True

        return request.user.user_roles.filter(
            role__name__in=['ADMIN', 'STOREKEEPER'],
            is_active=True
        ).exists()


class CanManageSales(permissions.BasePermission):
    """
    Permission for sales operations
    CASHIER can create and complete sales
    MANAGER/ADMIN can void and refund sales
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        #READ operations allowed for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        #CASHIER, MANAGER, ADMIN can create sales
        if request.user.is_superuser:
            return True

        return request.user.user_roles.filter(
            role_name__in=['CASHIER', 'MANAGER', 'ADMIN'],
            is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        """
        Object-level permissions for specific sale actions
        """
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        #Check the action being performed
        action = view.action

        #Cashier can complete their own sales
        if action == 'complete':
            return request.user.user_roles.filter(
                role__name__in=['CASHIER', 'MANAGER', 'ADMIN'],
                is_active=True
            ).exists()

        return True

class CanViewFinance(permissions.BasePermission):
    """
    Permission for viewing financial data
    Only ADMIN and MANAGER can view ledger entries
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return request.user.user_roles.filter(
            role__name__in=['ADMIN', 'MANAGER'],
            is_active=True
        ).exists()

class CanViewAudit(permissions.BasePermission):
    """
    Permission for viewing audit logs
    Only ADMIN can view audit logs
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return request.user.user_roles.filter(
            role__name='ADMIN',
            is_active=True
        ).exists()

#Helper function - check if user has specific role
def user_has_role(user, role_names):
    """
    Helper function to check if user has any of the specified roles
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if isinstance(role_names, str):
        role_names = [role_names]

        return user.user_roles.filter(
            role__name__in=role_names,
            is_active=True
        ).exists()