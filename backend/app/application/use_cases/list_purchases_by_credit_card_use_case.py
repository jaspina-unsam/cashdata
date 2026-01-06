from dataclasses import dataclass

from app.domain.entities.purchase import Purchase
from app.domain.repositories import IUnitOfWork


@dataclass(frozen=True)
class ListPurchasesByCreditCardQuery:
    """Query to list purchases by credit card"""

    credit_card_id: int
    user_id: int  # For authorization


class ListPurchasesByCreditCardUseCase:
    """
    Use case to list all purchases for a specific credit card.

    Returns purchases sorted by date (most recent first).
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: ListPurchasesByCreditCardQuery) -> list[Purchase]:
        """
        Execute the use case to list purchases by credit card.

        Args:
            query: The query containing credit card ID and user ID

        Returns:
            List of Purchase entities for the credit card

        Raises:
            ValueError: If credit card doesn't exist or doesn't belong to user
        """
        with self.unit_of_work as uow:
            # Verify credit card exists and belongs to user
            credit_card = uow.credit_cards.find_by_id(query.credit_card_id)
            if not credit_card:
                raise ValueError(
                    f"Credit card with ID {query.credit_card_id} not found"
                )
            if credit_card.user_id != query.user_id:
                raise ValueError(
                    f"Credit card {query.credit_card_id} does not belong to user {query.user_id}"
                )

            # Get purchases
            purchases = uow.purchases.find_by_credit_card_id(query.credit_card_id)

            # Sort by purchase date descending (most recent first)
            return sorted(purchases, key=lambda p: p.purchase_date, reverse=True)
