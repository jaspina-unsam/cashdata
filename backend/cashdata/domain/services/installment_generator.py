from datetime import date
from decimal import Decimal

from cashdata.domain.entities.installment import Installment
from cashdata.domain.entities.tarjeta_credito import CreditCard
from cashdata.domain.value_objects.money import Money
from cashdata.domain.exceptions.domain_exceptions import InvalidCalculation


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

        if total_amount.amount <= 0:
            raise InvalidCalculation(
                f"total_amount must be positive, got {total_amount.amount}"
            )

        # Calculate base amount and remainder
        base_amount = total_amount.amount // installments_count
        remainder = total_amount.amount % installments_count

        installments = []
        current_date = purchase_date

        for i in range(1, installments_count + 1):
            # First installment absorbs the remainder
            if i == 1:
                installment_amount = base_amount + remainder
            else:
                installment_amount = base_amount

            # Calculate billing period for this installment
            billing_period = credit_card.calculate_billing_period(current_date)

            # Calculate due date for the period
            due_date = credit_card.calculate_due_date(billing_period)

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

            # Move to next month for next installment calculation
            # Use the due date as reference for next period calculation
            # to handle month transitions correctly
            if i < installments_count:
                # Move current_date to next billing cycle
                # Add 32 days and set to day 1 to ensure we're in the next month
                year = int(billing_period[:4])
                month = int(billing_period[4:6])
                
                # Calculate next month
                next_month = month + 1
                next_year = year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                
                # Set current_date to close day of next period
                # This ensures proper period calculation for next installment
                try:
                    current_date = date(next_year, next_month, credit_card.billing_close_day)
                except ValueError:
                    # If close day doesn't exist in month (e.g., Feb 31)
                    # Use last day of month
                    from calendar import monthrange
                    last_day = monthrange(next_year, next_month)[1]
                    current_date = date(next_year, next_month, last_day)

        return installments
