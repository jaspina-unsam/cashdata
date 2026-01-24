from app.domain.repositories.iunit_of_work import IUnitOfWork


class DeletePurchaseUseCase:
    """Use case for deletion of purchases"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, purchase_id: int, user_id: int) -> None:
        """
        Delete a purchase and all its installments.

        Args:
            purchase_id: ID of the purchase to delete
            user_id: ID of the user who owns the purchase

        Raises:
            ValueError: If purchase doesn't exist or doesn't belong to user
        """
        with self._uow:
            purchase = self._uow.purchases.find_by_id(purchase_id)
            if purchase is None or purchase.user_id != user_id:
                raise ValueError(
                    f"Purchase with ID {purchase_id} not found for user {user_id}"
                )

            # Get all installments for this purchase
            installments = self._uow.installments.find_by_purchase_id(purchase_id)
            
            # Delete budget expenses associated with each installment
            for installment in installments:
                installment_expenses = self._uow.budget_expenses.find_by_installment_id(installment.id)
                for expense in installment_expenses:
                    self._uow.budget_expenses.delete(expense.id)

            # Delete budget expenses associated directly with the purchase
            budget_expenses = self._uow.budget_expenses.find_by_purchase_id(purchase_id)
            for expense in budget_expenses:
                self._uow.budget_expenses.delete(expense.id)

            # Delete the purchase (cascade will delete installments)
            self._uow.purchases.delete(purchase_id)
            self._uow.commit()
