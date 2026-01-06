from dataclasses import dataclass

from app.domain.entities.installment import Installment
from app.domain.repositories import IUnitOfWork


@dataclass(frozen=True)
class ListInstallmentsByPurchaseQuery:
    """Query to list installments by purchase"""

    purchase_id: int
    user_id: int  # For authorization


class ListInstallmentsByPurchaseUseCase:
    """
    Use case to list all installments for a specific purchase.

    Returns installments sorted by installment number.
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: ListInstallmentsByPurchaseQuery) -> list[Installment]:
        """
        Execute the use case to list installments by purchase.

        Args:
            query: The query containing purchase ID and user ID

        Returns:
            List of Installment entities for the purchase

        Raises:
            ValueError: If purchase doesn't exist or doesn't belong to user
        """
        with self.unit_of_work as uow:
            # Verify purchase exists and belongs to user
            purchase = uow.purchases.find_by_id(query.purchase_id)
            if not purchase:
                raise ValueError(f"Purchase with ID {query.purchase_id} not found")
            if purchase.user_id != query.user_id:
                raise ValueError(
                    f"Purchase {query.purchase_id} does not belong to user {query.user_id}"
                )

            # Get installments
            installments = uow.installments.find_by_purchase_id(query.purchase_id)

            # Sort by installment number
            return sorted(installments, key=lambda i: i.installment_number)
