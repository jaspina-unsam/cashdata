from datetime import date
from decimal import Decimal
from typing import Union
from dateutil.relativedelta import relativedelta

from app.domain.entities.installment import Installment
from app.domain.entities.credit_card import CreditCard
from app.domain.value_objects.money import Money
from app.domain.value_objects.dual_money import DualMoney
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
        total_amount: Union[DualMoney, Money],
        installments_count: int,
        purchase_date: date,
        credit_card: CreditCard,
    ) -> list[Installment]:
        """
        Generate installments for a purchase.

        Args:
            purchase_id: ID of the purchase
            total_amount: Total amount to split (DualMoney or Money for backward compatibility)
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
        # Convert Money to DualMoney for uniform handling
        if isinstance(total_amount, Money):
            total_amount = DualMoney(
                primary_amount=total_amount.amount,
                primary_currency=total_amount.currency,
            )
        
        # Validate inputs
        if installments_count < 1:
            raise InvalidCalculation(
                f"installments_count must be >= 1, got {installments_count}"
            )

        if total_amount.primary_amount == 0:
            raise InvalidCalculation(
                f"total_amount cannot be zero, got {total_amount.primary_amount}"
            )

        # Calculate base amount per installment using proper Decimal division
        # to preserve cents precision
        base_amount = (total_amount.primary_amount / Decimal(installments_count)).quantize(
            Decimal("0.01")
        )

        # Calculate remainder after distributing base amounts
        total_distributed = base_amount * Decimal(installments_count)
        remainder = total_amount.primary_amount - total_distributed
        
        # Calculate secondary amounts if dual-currency
        base_secondary_amount = None
        remainder_secondary = None
        if total_amount.is_dual_currency():
            base_secondary_amount = (total_amount.secondary_amount / Decimal(installments_count)).quantize(
                Decimal("0.01")
            )
            total_secondary_distributed = base_secondary_amount * Decimal(installments_count)
            remainder_secondary = total_amount.secondary_amount - total_secondary_distributed

        installments = []

        initial_billing_period = credit_card.calculate_billing_period(purchase_date)

        for i in range(1, installments_count + 1):
            # First installment absorbs the remainder to ensure exact total
            if i == 1:
                installment_amount = base_amount + remainder
                if base_secondary_amount is not None:
                    installment_secondary_amount = base_secondary_amount + remainder_secondary
                else:
                    installment_secondary_amount = None
            else:
                installment_amount = base_amount
                installment_secondary_amount = base_secondary_amount

            # For each installment, add (i-1) months to the initial period
            # Parse initial period to a date (use day 1 for calculation)
            year = int(initial_billing_period[:4])
            month = int(initial_billing_period[4:])
            period_date = date(year, month, 1)

            # Add months
            installment_period_date = period_date + relativedelta(months=(i - 1))

            # Format back to YYYYMM
            billing_period = (
                f"{installment_period_date.year:04d}{installment_period_date.month:02d}"
            )
            
            # Create DualMoney for installment
            if installment_secondary_amount is not None:
                installment_dual_money = DualMoney(
                    primary_amount=installment_amount,
                    primary_currency=total_amount.primary_currency,
                    secondary_amount=installment_secondary_amount,
                    secondary_currency=total_amount.secondary_currency,
                    exchange_rate=total_amount.exchange_rate,
                )
            else:
                installment_dual_money = DualMoney(
                    primary_amount=installment_amount,
                    primary_currency=total_amount.primary_currency,
                )

            # Create installment
            installment = Installment(
                id=None,
                purchase_id=purchase_id,
                installment_number=i,
                total_installments=installments_count,
                amount=installment_dual_money,
                billing_period=billing_period,
                manually_assigned_statement_id=None
            )

            installments.append(installment)

        return installments
