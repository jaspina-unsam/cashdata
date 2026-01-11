from dataclasses import dataclass
from typing import Optional

from app.domain.entities.purchase import Purchase
from app.domain.repositories.iunit_of_work import IUnitOfWork


@dataclass(frozen=True)
class GetPurchaseByIdQuery:
    """Query to get a purchase by ID"""

    purchase_id: int
    user_id: int  # For authorization - ensure user owns the purchase


class GetPurchaseByIdUseCase:
    """
    Use case to retrieve a purchase by its ID.

    Validates that the purchase belongs to the requesting user.
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: GetPurchaseByIdQuery) -> Optional[Purchase]:
        """
        Execute the use case to get a purchase by ID.

        Args:
            query: The query containing purchase ID and user ID

        Returns:
            Purchase entity if found and belongs to user, None otherwise
        """
        with self.unit_of_work as uow:
            purchase = uow.purchases.find_by_id(query.purchase_id)

            # Verify purchase exists and belongs to user
            if purchase and purchase.user_id == query.user_id:
                return purchase

            return None
