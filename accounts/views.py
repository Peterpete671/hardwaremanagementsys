"""
Views for Accounts app with role-based permissions.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db import transaction

from .models import User, Role, UserRole
from .serializers import (
    UserSerializer, UserCreateSerializer, UserWithRolesSerializer,
    RoleSerializer, UserRoleSerializer
)
from .permissions import CanManageUsers, IsAdmin


class AuthViewSet(viewsets.ViewSet):
    """
    Handles user authentication (login/logout).
    No role restrictions on login/logout.
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Authenticate user and return token."""
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'User account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )

        token, created = Token.objects.get_or_create(user=user)
        serializer = UserWithRolesSerializer(user)

        return Response({
            'token': token.key,
            'user': serializer.data
        })

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user by deleting their token."""
        if request.user.is_authenticated:
            Token.objects.filter(user=request.user).delete()
            return Response({'message': 'Successfully logged out'})

        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management.
    Only ADMIN can create/update/delete users.
    All authenticated users can view users.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, CanManageUsers]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserWithRolesSerializer
        return UserSerializer

    def get_queryset(self):
        if self.action == 'retrieve':
            return User.objects.prefetch_related('user_roles__role')
        return User.objects.all()

    @action(detail=True, methods=['post'], url_path='roles', permission_classes=[IsAdmin])
    def assign_role(self, request, pk=None):
        """
        Assign a role to a user.
        Only ADMIN can assign roles.
        """
        user = self.get_object()
        role_id = request.data.get('role_id')

        if not role_id:
            return Response(
                {'error': 'role_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response(
                {'error': 'Role not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'is_active': True}
        )

        if not created:
            if not user_role.is_active:
                user_role.is_active = True
                user_role.save()
                message = 'Role reactivated'
            else:
                message = 'Role already assigned'
        else:
            message = 'Role assigned successfully'

        serializer = UserRoleSerializer(user_role)
        return Response({
            'message': message,
            'user_role': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='roles/(?P<role_id>[^/.]+)', permission_classes=[IsAdmin])
    def remove_role(self, request, pk=None, role_id=None):
        """
        Remove (deactivate) a role from a user.
        Only ADMIN can remove roles.
        """
        user = self.get_object()

        try:
            user_role = UserRole.objects.get(user=user, role_id=role_id)
        except UserRole.DoesNotExist:
            return Response(
                {'error': 'Role assignment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        user_role.is_active = False
        user_role.save()

        return Response({'message': 'Role removed successfully'})


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Role management (read-only).
    All authenticated users can view roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]