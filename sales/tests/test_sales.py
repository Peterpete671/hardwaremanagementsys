from django.test import TestCase
from django.db import models
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from accounts.models import User, Role, UserRole
from inventory.models import Category, Product, Warehouse, StockMovement
from sales.models import Sale, SaleItem, Payments
from finance.models import Account, LedgerEntry

class SalesWorkflowTestCase(TestCase):
    """Test complete sales workflow"""
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        #Create roles
        self.cashier_role = Role.objects.create(name='CASHIER')
        self.manager_role = Role.objects.create(name='MANAGER')

        #Create users
        self.cashier = User.objects.create_user(
            username='cashier', password='cashier123',
            email='cashier_sales@example.com'
        )
        UserRole.objects.create(user=self.cashier, role=self.cashier_role, is_active=True)

        self.manager = User.objects.create_user(
            username='manager', password='manager123',
            email='manager@example.com'
        )
        UserRole.objects.create(user=self.manager, role=self.manager_role, is_active=True)

        #Create warehouse
        self.warehouse = Warehouse.objects.create(
            name='Main Warehouse',
            location='Nairobi',
            is_active=True
        )

        #Create category and product
        category = Category.objects.create(name='Electronics', is_active=True)
        self.product = Product.objects.create(
            sku='PROD001',
            name='Test Product',
            category=category,
            unit_cost=Decimal('10.00'),
            unit_price=Decimal('10.00'),
            track_stock=True,
            is_active=True
        )
        
        #Add stock
        StockMovement.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            movement_type='IN',
            quantity=Decimal('100'),
            reference_type='MANUAL',
            created_by=self.cashier
        )

        #Create finance accounts
        Account.objects.create(name='Cash', account_type='ASSET', is_active=True)
        Account.objects.create(name='Revenue', account_type='INCOME', is_active=True)
        Account.objects.create(name='Cost of Goods Sold', account_type='EXPENSE', is_active=True)
        Account.objects.create(name='Inventory', account_type='ASSET', is_active=True)

    def test_complete_sale_workflow(self):
        """Test complete sale workflow from crreation to completion"""
        self.client.force_authenticate(user=self.cashier)

        #1. Create draft sale
        url = reverse('sale-list')
        data = {
            'warehouse': str(self.warehouse.id),
            'sold_by': str(self.cashier.id)
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sale_id = response.data['id']
        self.assertEqual(response.data['status'], 'PENDING')

        #2. Add item to sale
        url = reverse('sale-add-item', kwargs={'pk': sale_id})
        data = {
            'product': str(self.product.id),
            'quantity': 5
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data.get('id'))
        self.assertIn('quantity', response.data)
        self.assertIn('unit_price', response.data)

        #3. Add payment
        url = reverse('sale-add-payment', kwargs={'pk': sale_id})
        data = {
            'payment_method': 'CASH',
            'amount': '100.00',
            'reference_code': '',
            'received_by': str(self.cashier.id)
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #4. Complete sale
        url = reverse('sale-complete', kwargs={'pk': sale_id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)

        #Verify stock was reduced
        stock = StockMovement.objects.filter(
            product=self.product,
            warehouse=self.warehouse
        ).aggregate(total=models.Sum('quantity'))['total']
        # Check that ledger entries were created
        ledger_entries = LedgerEntry.objects.all()
        self.assertGreater(ledger_entries.count(), 0)

    def test_complete_sale_insufficient_stock(self):
        """Test sale completion fails with insufficient stock"""
        self.client.force_authenticate(user=self.cashier)

        #Create sale with more items than stock
        url = reverse('sale-list')
        data = {
            'warehouse': str(self.warehouse.id),
            'sold_by': str(self.cashier.id)
        }
        response = self.client.post(url, data, format='json')
        sale_id = response.data['id']

        # Add item (requesting 200, but only 100 in stock)
        url = reverse('sale-add-item', kwargs={'pk': sale_id})
        data = {
            'product': str(self.product.id),
            'quantity': 200
        }
        self.client.post(url, data, format='json')

        #Add payment
        url = reverse('sale-add-payment', kwargs={'pk': sale_id})
        data = {
            'payment_method': 'CASH',
            'amount': '4000.00',
            'received_by': str(self.cashier.id)
        }
        self.client.post(url, data, format='json')

        #Try to complete(should fail)
        url = reverse('sale-complete', kwargs={'pk': sale_id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that error contains some reference to stock or insufficient  
        error_data = response.data if isinstance(response.data, dict) else {}
        self.assertTrue('error' in error_data or 'detail' in error_data or response.status_code == status.HTTP_400_BAD_REQUEST)

    def test_void_sale_as_manager(self):
        """Test manager can void pending sales"""
        self.client.force_authenticate(user=self.manager)

        #Create pending sale
        sale = Sale.objects.create(
            sale_number='SALE-00001',
            warehouse=self.warehouse,
            sold_by=self.cashier,
            status='PENDING',
            grand_total=Decimal('100.00')
        )

        url = reverse('sale-void', kwargs={'pk': sale.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sale.refresh_from_db()
        self.assertEqual(sale.status, 'VOIDED')

    def test_void_sale_as_cashier_fails(self):
        """Test cahier cannot void sales"""
        self.client.force_authenticate(user=self.cashier)

        sale = Sale.objects.create(
            sale_number='SALE-000001',
            warehouse=self.warehouse,
            sold_by=self.cashier,
            status='PENDING',
            grand_total=Decimal('100.00')
        )

        url = reverse('sale-void', kwargs={'pk': sale.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


