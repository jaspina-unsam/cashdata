from datetime import date
from decimal import Decimal
from dateutil.relativedelta import relativedelta

from app.domain.entities.installment import Installment
from app.domain.entities.credit_card import CreditCard
from app.domain.value_objects.money import Money
from app.domain.exceptions.domain_exceptions import InvalidCalculation


class InstallmentGenerator:
    """
    Domain Service to generate installments for a purchase.

    Splits total amount evenly across installments with the first
    installment absorbing any remainder to ensure exact sum.
    """

    @staticmethod
    def generate_installments(
        purchase_id: int,
        total_amount: Money,
        installments_count: int,
        purchase_date: date,
        credit_card: CreditCard,
    ) -> list[Installment]:
        """
        Generate installments for a purchase.

        Args:
            purchase_id: ID of the purchase
            total_amount: Total amount to split
            installments_count: Number of installments (>= 1)
            purchase_date: Date of purchase
            credit_card: Credit card with billing configuration

        Returns:
            List of Installment entities

        Raises:
            InvalidCalculation: If validation fails

        Example:
            10000 ARS / 3 installments = [3334, 3333, 3333]
            First installment absorbs remainder (3333 + 1 = 3334)
        """
        # Validate inputs
        if installments_count < 1:
            raise InvalidCalculation(
                f"installments_count must be >= 1, got {installments_count}"
            )

        if total_amount.amount == 0:
            raise InvalidCalculation(
                f"total_amount cannot be zero, got {total_amount.amount}"
            )

        # Calculate base amount per installment using proper Decimal division
        # to preserve cents precision
        base_amount = (total_amount.amount / Decimal(installments_count)).quantize(
            Decimal("0.01")
        )

        # Calculate remainder after distributing base amounts
        total_distributed = base_amount * Decimal(installments_count)
        remainder = total_amount.amount - total_distributed

        installments = []

        # Calculate initial statement close and due dates based on purchase date
        # We'll use the old calculate_billing_period to determine which statement this falls into
        initial_statement_month = credit_card.calculate_billing_period(purchase_date)
        initial_due_date = credit_card.calculate_due_date(initial_statement_month)

        for i in range(1, installments_count + 1):
            # First installment absorbs the remainder to ensure exact total
            if i == 1:
                installment_amount = base_amount + remainder
            else:
                installment_amount = base_amount

            # Calculate due date for this installment (i-1 months after initial)
            due_date = initial_due_date + relativedelta(months=(i - 1))

            # Calculate billing_period from due_date minus 1 month
            # This ensures the period represents when charges were made
            due_year = due_date.year
            due_month = due_date.month

            period_month = due_month - 1
            period_year = due_year
            if period_month < 1:
                period_month = 12
                period_year -= 1

            billing_period = f"{period_year:04d}{period_month:02d}"

            # Create installment
            installment = Installment(
                id=None,
                purchase_id=purchase_id,
                installment_number=i,
                total_installments=installments_count,
                amount=Money(installment_amount, total_amount.currency),
                billing_period=billing_period,
                due_date=due_date,
            )

            installments.append(installment)

        return installments
