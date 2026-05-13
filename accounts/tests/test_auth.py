"""
Login, logout and token generation
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User, Role, UserRole

class AuthenticationTestCase(TestCase):
    """Test authentication endpoints"""

    def setUp(self):
        """Set up test client and test user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_login_success(self):
        """Test successful login returns token"""
        url = reverse('auth-login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_login_invalid_credentials(self):
        """Test login with invalid credential fails"""
        url = reverse('auth-login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_login_missing_fields(self):
        """Test login without username or password fails"""
        url = reverse('auth-login')
        data = {'username': 'testuser'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user(self):
        """Test login with inactive user fails"""
        self.user.is_active = False
        self.user.save()

        url = reverse('auth-login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        """Test logout deletes token"""
        self.client.force_authenticate(user=self.user)

        url = reverse('auth-logout')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_logout_unauthenticated(self):
        """Test logout without authentication fails"""
        url = reverse('auth-logout')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)