from dataclasses import dataclass
from datetime import date

from cashdata.domain.entities.purchase import Purchase
from cashdata.domain.repositories import IUnitOfWork


@dataclass(frozen=True)
class ListPurchasesByDateRangeQuery:
    """Query to list purchases by date range"""

    user_id: int
    start_date: date
    end_date: date


class ListPurchasesByDateRangeUseCase:
    """
    Use case to list purchases within a date range.

    Returns purchases sorted by date (most recent first).
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: ListPurchasesByDateRangeQuery) -> list[Purchase]:
        """
        Execute the use case to list purchases by date range.

        Args:
            query: The query containing user ID and date range

        Returns:
            List of Purchase entities within the date range

        Raises:
            ValueError: If start_date is after end_date
        """
        if query.start_date > query.end_date:
            raise ValueError("start_date must be before or equal to end_date")

        with self.unit_of_work as uow:
            # Get all purchases for user
            all_purchases = uow.purchases.find_by_user_id(query.user_id)

            # Filter by date range
            filtered_purchases = [
                p
                for p in all_purchases
                if query.start_date <= p.purchase_date <= query.end_date
            ]

            # Sort by purchase date descending (most recent first)
            return sorted(
                filtered_purchases, key=lambda p: p.purchase_date, reverse=True
            )
