from dataclasses import dataclass

from app.domain.entities.purchase import Purchase
from app.domain.repositories import IUnitOfWork


@dataclass(frozen=True)
class ListPurchasesByPaymentMethodQuery:
    """Query to list purchases by payment method"""

    payment_method_id: int
    user_id: int  # For authorization


class ListPurchasesByPaymentMethodUseCase:
    """
    Use case to list all purchases for a specific payment method.

    Returns purchases sorted by date (most recent first).
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: ListPurchasesByPaymentMethodQuery) -> list[Purchase]:
        """
        Execute the use case to list purchases by payment method.

        Args:
            query: The query containing payment method ID and user ID

        Returns:
            List of Purchase entities for the payment method

        Raises:
            ValueError: If payment method doesn't exist or doesn't belong to user
        """
        with self.unit_of_work as uow:
            # Verify payment method exists and belongs to user
            payment_method = uow.payment_methods.find_by_id(query.payment_method_id)
            if not payment_method:
                raise ValueError(
                    f"Payment method with ID {query.payment_method_id} not found"
                )
            if payment_method.user_id != query.user_id:
                raise ValueError(
                    f"Payment method {query.payment_method_id} does not belong to user {query.user_id}"
                )

            # Get purchases
            purchases = uow.purchases.find_by_payment_method_id(query.payment_method_id)

            # Sort by purchase date descending (most recent first)
            return sorted(purchases, key=lambda p: p.purchase_date, reverse=True)
