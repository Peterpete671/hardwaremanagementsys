"""
FINANCE APP - Money Truth
Purpose: Simple Ledger system for financial tracking
Currently single-entry, structured for future double-entry upgrade.
"""
import uuid
from django.db import models


class Account(models.Model):
    """
    Chart of accounts for the ledger.

    SIMPLE STRUCTURE: Cash, Revenue, Inventory, COGS, etc.
    Account types follow accounting principles:
    -ASSET: Cash, Inventory, Accounts Receivable
    -LIABILITY: Accounts Payable, Loans
    -INCOME: Sales Revenue
    -EXPENSE: Cost of Goods Sold, Operating Expenses
    """

    ACCOUNT_TYPE_CHOICES = [
        ('ASSET', 'Asset'),
        ('LIABILITY', 'Liability'),
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        help_text="Account Name (e.g. Cash, Revenue, Inventory, COGS)"
    )

    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        db_index=True
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table= 'account'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    def __str__(self):
        return f"{self.name} - ({self.account_type})"


class LedgerEntry(models.Model):
    """
    Financial ledger entries
    Currently single-entry but structured for future double-entry upgrade.
    Amount is signed: positive for increases, negative for decreases
    *Interpretation depends on account type.

    Reference fields link entries to source transactions (Sale, Refund, etc.).
    These records are immutable for audit and legal compliance.
    """

    REFERENCE_TYPE_CHOICES = [
        ('SALE', 'sale'),
        ('REFUND', 'refund'),
        ('ADJUSTMENT', 'adjustment'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='ledger_entries'
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Signed amount: positive/negative based on account type"
    )

    reference_type = models.CharField(
        max_length=20,
        choices=REFERENCE_TYPE_CHOICES,
        db_index=True
    )

    reference_id = models.UUIDField(
        db_index=True,
        help_text="Links to Sale, Refund, or other source transaction"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table= 'ledger_entry'
        verbose_name = 'Ledger Entry'
        verbose_name_plural = 'Ledger Entries'
        indexes = [
            models.Index(fields=['account', 'created_at']),
            models.Index(fields=['reference_type', 'reference_id']),
        ]

    def __str__(self):
        return f"{self.account.name} - {self.amount} - {self.reference_type}"

