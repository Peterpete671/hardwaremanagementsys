"""
Views for Accounts app
Handles authentication, users, and role management.
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

class AuthViewSet(viewsets.ViewSet):
    """
    Handles User authentication (login and logout)
    Endpoints
    -POST /api/auth/login/
    -POST /api/auth/logout/
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Authenticate user and return tokens
        POST /api/auth/login
        """
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

        #Get/create token
        token, created = Token.objects.get_or_create(user=user)

        #Get user with roles
        serializer = UserWithRolesSerializer(user)

        return Response({
            'token': token.key,
            'user': serializer.data
        })
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Logout user - delete token
        POST /api/auth/logout
        """

        if request.user.is_authenticated:
            Token. objects.filter(user=request.user).delete()
            return Response({'message': 'Successfully logged out'})

        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User Management

    Endpoints:
    -GET /api/users/
    -POST /api/users/
    -GET /api/users/{id}/
    -PUT /api/users/{id}/
    -PATCH /api/users/{id}/
    -DELETE /api/users/{id}/
    """

    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserWithRolesSerializer
        return UserSerializer

    def get_queryset(self):
        """Optimize query with role prefetching"""
        if self.action == 'retrieve':
            return User.objects.prefetch_related('user_roles__role')
        return User.objects.all()

    @action(detaail=True, methods=['post'], url_path='roles')
    def assign_role(self, request, pk=None):
        """
        Assign a role to a user.
        POST: /api/users/{id}/roles/
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

        #Check if assignment already exists
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'is_active': True}
        )

        if not created:
            # Reactivate if not active
            if not user_role.is_active:
                user_role.is_active = True
                user_role.save()
                message = 'Role reactivated'
            else:
                message = 'Role assigned successfully'

            serializer = UserRoleSerializer(user_role)
            return Response({
                'message': message,
                'user_role': serializer.data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        @action(detail=True, methods=['delete'], url_path='roles/(?P<role_id>[^/.]+)')
        def remove_role(self, request, pk=None, role_id=None):
            """
            Remove/deactivate a role from a user
            DELETE /api/users/{id}/roles/{role_id}/
            """

            user = self.get_object()

            try:
                user_role = UserRole.objects.get(user=user, role_id=role_id)
            except UserRole.DoesNotExist:
                return Response(
                    {'error': 'Role assignment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            #Deactivate instead of delete for audit trail
            user_role.is_active = False
            user_role.save()

            return Response({'message': 'Role removed successfully'})



class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Role management
    Read only
    -GET /api/roles/
    -GET /api/roles/{id}/
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]





