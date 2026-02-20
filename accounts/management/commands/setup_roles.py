"""
Management command to create initial system roles.

Usage:
    python manage.py setup_roles
"""

from django.core.management.base import BaseCommand
from accounts.models import Role


class Command(BaseCommand):
    help = 'Creates initial system roles (ADMIN, MANAGER, CASHIER, STOREKEEPER)'

    def handle(self, *args, **options):
        roles_data = [
            {
                'name': 'ADMIN',
                'description': 'Full system access. Can manage users, view all reports, perform all operations.'
            },
            {
                'name': 'MANAGER',
                'description': 'Can manage sales, view financial reports, manage inventory, void/refund sales.'
            },
            {
                'name': 'CASHIER',
                'description': 'Can create and complete sales, process payments, view products.'
            },
            {
                'name': 'STOREKEEPER',
                'description': 'Can manage inventory, adjust stock, manage warehouses and products.'
            },
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created role: {role.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Role already exists: {role.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n✓ Role setup complete!')
        )