"""
Product management tests
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from accounts.models import User, UserRole, Role
from inventory.models import Category, Product

class ProductManagementTestCase(TestCase):
    """Test product CRUD operations"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        #Create roles
        self.admin_role = Role.objects.create(name='ADMIN')
        self.storekeeper_role = Role.objects.create(name='STOREKEEPER')
        self.cashier_role = Role.objects.create(name='CASHIER')

        #Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        UserRole.objects.create(user=self.admin_user, role=self.admin_role, is_active=True)

        self.storekeeper = User.objects.create_user(
            username='storekeeper',
            password='store123',
            email='storekeeper@example.com'
        )
        UserRole.objects.create(user=self.storekeeper, role=self.storekeeper_role, is_active=True)

        self.cashier = User.objects.create_user(
            username='cashier', password='cashier123',
            email='cashier@example.com'
        )

        UserRole.objects.create(user=self.cashier, role=self.cashier_role, is_active=True)

        #Create category
        self.category = Category.objects.create(
            name='Electronics',
            is_active=True
        )

    def test_create_product_as_storekeeper(self):
        """Test storekeeper can create products"""
        self.client.force_authenticate(user=self.storekeeper)

        url = reverse('product-list')
        data = {
            'sku': 'PROD001',
            'name': 'Test Product',
            'category': str(self.category.id),
            'unit_cost': '10.00',
            'unit_price': '20.00',
            'track_stock': True,
            'is_active': True
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

        product = Product.objects.first()
        self.assertEqual(product.sku, 'PROD001')
        self.assertEqual(product.unit_price, Decimal('20.00'))

    def test_create_product_as_cashier_fails(self):
        """Test cashier cannot create products"""
        self.client.force_authenticate(user=self.cashier)

        url = reverse('product-list')
        data = {
            'sku': 'PROD001',
            'name': 'Test Product',
            'category': str(self.category.id),
            'unit_cost': '10.00',
            'unit_price': '20.00',
            'track_stock': True,
            'is_active': True            
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_product_with_filters(self):
        """Test listing product with filters"""
        self.client.force_authenticate(user=self.cashier)

        #Create products
        Product.objects.create(
            sku='PROD001',
            name='Product 1',
            category=self.category,
            unit_cost=10,
            unit_price=20,
            is_active=True
        )

        Product.objects.create(
            sku='PROD002',
            name='Product 2',
            category=self.category,
            unit_cost=15,
            unit_price=30,
            is_active=False
        )

        #List all products
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        #Filter by active
        url = reverse('product-list') + '?is_active=true'
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)

        #Search by SKU
        url = reverse('product-list') + '?search=PROD001'
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)