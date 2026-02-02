"""
Serializers - Accounts
Handles User, Role, and UserRole serialization for API.
"""

from rest_framework import serializers
from .models import User, Role, UserRole

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, excludes password for security in read operations.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_staff','created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating users with password
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        Fields = ['id', 'username', 'email', 'password', 'is_active', 'is_staff']
        read_only_fields = ['id']

    def create(self, validated_data):
        """
        Create user with hashed password
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model
    """
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for UserRole assignments
    """
    user_username = serializers.CharField(
        source='user.username',
        read_only=True
    )
    role_name = serializers.CharField(
        source='role.name',
        read_only=True
    )

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'user_username', 'role', 'role_name', 'is_active', 'assigned_at']
        read_only_fields = ['id', 'assigned_at']

class UserWithRolesSerializer(serializers.ModelSerializer):
    """
    User serializer with nested active roles
    Useful for displaying user with their current permissions.
    """
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_staff', 'roles', 'created_at']
        read_only_fields = ['id', 'created_at']

    @staticmethod
    def get_roles(obj):
        """
        Get all the active roles for this user
        """
        active_roles = obj.user_roles.filter(is_active=True).select_related('role')
        return [{'id': str(ur.role.id), 'name': ur.role.name} for ur in active_roles]