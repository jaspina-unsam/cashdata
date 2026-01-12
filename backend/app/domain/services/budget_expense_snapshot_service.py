from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.domain.entities.purchase import Purchase
from app.domain.entities.installment import Installment
from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.money import Money


@dataclass(frozen=True)
class ExpenseSnapshot:
    """
    Snapshot of expense data captured at the time it's added to budget.

    This ensures budget calculations remain consistent even if original
    purchase/installment data changes.
    """
    amount: Money
    currency: str
    description: str
    date: date
    payment_method_name: Optional[str]


class BudgetExpenseSnapshotService:
    """
    Domain Service to create snapshots of expenses for budget persistence.

    Creates consistent snapshots from Purchase or Installment entities
    that can be stored in budget_expenses table.
    """

    def create_snapshot_from_purchase(
        self,
        purchase: Purchase,
        payment_method: Optional[PaymentMethod] = None
    ) -> ExpenseSnapshot:
        """
        Create snapshot from a Purchase entity.

        Args:
            purchase: The purchase to snapshot
            payment_method: Optional payment method for name

        Returns:
            ExpenseSnapshot with purchase data
        """
        payment_method_name = payment_method.name if payment_method else None

        return ExpenseSnapshot(
            amount=purchase.total_amount,
            currency=purchase.total_amount.currency,
            description=purchase.description,
            date=purchase.purchase_date,
            payment_method_name=payment_method_name
        )

    def create_snapshot_from_installment(
        self,
        installment: Installment,
        payment_method: Optional[PaymentMethod] = None
    ) -> ExpenseSnapshot:
        """
        Create snapshot from an Installment entity.

        Args:
            installment: The installment to snapshot
            payment_method: Optional payment method for name

        Returns:
            ExpenseSnapshot with installment data
        """
        payment_method_name = payment_method.name if payment_method else None

        # Generate description for installment
        description = f"Installment {installment.installment_number}/{installment.total_installments}"
        
        # Use the first day of the billing period as the date
        year = int(installment.billing_period[:4])
        month = int(installment.billing_period[4:])
        expense_date = date(year, month, 1)

        # For installments, use the installment's amount and generated date
        return ExpenseSnapshot(
            amount=installment.amount,
            currency=installment.amount.currency,
            description=description,
            date=expense_date,
            payment_method_name=payment_method_name
        )