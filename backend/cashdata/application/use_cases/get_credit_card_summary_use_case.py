from dataclasses import dataclass
from decimal import Decimal

from cashdata.domain.entities.installment import Installment
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.domain.repositories import IUnitOfWork


@dataclass(frozen=True)
class GetCreditCardSummaryQuery:
    """Query to get summary for a credit card in a specific billing period"""

    credit_card_id: int
    user_id: int  # For authorization
    billing_period: str  # Format: YYYYMM


@dataclass(frozen=True)
class CreditCardSummary:
    """Summary of credit card usage for a billing period"""

    credit_card_id: int
    billing_period: str
    total_amount: Money
    installments_count: int
    installments: list[Installment]


class GetCreditCardSummaryUseCase:
    """
    Use case to get a summary of credit card usage for a billing period.

    Returns:
    - Total amount due
    - Number of installments
    - List of all installments for the period
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: GetCreditCardSummaryQuery) -> CreditCardSummary:
        """
        Execute the use case to get credit card summary.

        Args:
            query: The query containing card ID, user ID, and billing period

        Returns:
            CreditCardSummary with totals and installment details

        Raises:
            ValueError: If credit card doesn't exist or doesn't belong to user
        """
        with self.unit_of_work as uow:
            # Validate credit card exists and belongs to user
            credit_card = uow.credit_cards.find_by_id(query.credit_card_id)
            if not credit_card:
                raise ValueError(
                    f"Credit card with ID {query.credit_card_id} not found"
                )
            if credit_card.user_id != query.user_id:
                raise ValueError(
                    f"Credit card {query.credit_card_id} does not belong to user {query.user_id}"
                )

            # Get all installments for this card and period
            installments = uow.installments.find_by_credit_card_and_period(
                query.credit_card_id, query.billing_period
            )

            # Calculate total amount
            if installments:
                # All installments should have same currency
                currency = installments[0].amount.currency
                total_amount = Money(
                    sum(inst.amount.amount for inst in installments), currency
                )
            else:
                # Default to ARS with zero amount
                total_amount = Money(Decimal("0"), Currency.ARS)

            return CreditCardSummary(
                credit_card_id=query.credit_card_id,
                billing_period=query.billing_period,
                total_amount=total_amount,
                installments_count=len(installments),
                installments=installments,
            )
