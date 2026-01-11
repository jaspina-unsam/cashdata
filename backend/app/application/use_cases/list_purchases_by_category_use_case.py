from dataclasses import dataclass

from app.domain.entities.purchase import Purchase
from app.domain.repositories.iunit_of_work import IUnitOfWork


@dataclass(frozen=True)
class ListPurchasesByCategoryQuery:
    """Query to list purchases by category"""

    category_id: int
    user_id: int  # For authorization


class ListPurchasesByCategoryUseCase:
    """
    Use case to list all purchases for a specific category.

    Returns purchases sorted by date (most recent first).
    Only returns purchases belonging to the specified user.
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: ListPurchasesByCategoryQuery) -> list[Purchase]:
        """
        Execute the use case to list purchases by category.

        Args:
            query: The query containing category ID and user ID

        Returns:
            List of Purchase entities for the category, filtered by user
        """
        with self.unit_of_work as uow:
            # Get all purchases for the user
            all_purchases = uow.purchases.find_by_user_id(query.user_id)

            # Filter by category
            category_purchases = [
                p for p in all_purchases if p.category_id == query.category_id
            ]

            # Sort by purchase date descending (most recent first)
            return sorted(
                category_purchases, key=lambda p: p.purchase_date, reverse=True
            )
