"""
User management tests: CRUD operations, role assignments
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User, UserRole, Role

class UserManagementTestCase(TestCase):
    """Test user CRUD operations"""

    def setUp(self):
        """Set up test client, admin user, and roles"""
        self.client = APIClient()

        #Create admin role
        self.admin_role = Role.objects.create(
            name='ADMIN',
            description='Administrator'
        )

        #Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@example.com',
            is_staff=True
        )

        UserRole.objects.create(
            user=self.admin_user,
            role=self.admin_role,
            is_active=True
        )

        #Create regular user
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regular123',
            email='regular@example.com'
        )

    def test_create_user_as_admin(self):
        """Test admin can create users"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_create_user_as_regular_user_fails(self):
        """Test regular user cannot create users"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response =self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users(self):
        """Test authenticated users can list users"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('user-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_user_with_roles(self):
        """Test retrieving user with roles"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('user-detail', kwargs={'pk': self.admin_user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('roles', response.data)
        self.assertEqual(len(response.data['roles']), 1)
        self.assertEqual(response.data['roles'][0]['name'], 'ADMIN')

    def test_assign_role_to_user(self):
        """Test admin can assign role to users"""
        self.client.force_authenticate(user=self.admin_user)

        #Create cashier role
        cashier_role = Role.objects.create(name='CASHIER', description='Cashier')

        url = reverse('user-assign-role', kwargs={'pk': self.regular_user.pk})
        data = {'role_id': str(cashier_role.id)}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserRole.objects.filter(
                user=self.regular_user,
                role=cashier_role,
                is_active=True
            ).exists()
        )

    def test_remove_role_from_user(self):
        """Test admin can remove roles from users"""
        self.client.force_authenticate(user=self.admin_user)

        #Assign role first
        cashier_role = Role.objects.create(name='CASHIER', description='Cashier')
        user_role = UserRole.objects.create(
            user=self.regular_user,
            role=cashier_role,
            is_active=True
        )

        url = reverse('user-remove-role', kwargs={
            'pk': self.regular_user.pk,
            'role_id': str(cashier_role.id)
        })
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_role.refresh_from_db()
        self.assertFalse(user_role.is_active)
