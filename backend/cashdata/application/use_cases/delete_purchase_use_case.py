from cashdata.domain.repositories.iunit_of_work import IUnitOfWork


class DeletePurchaseUseCase:
    """Use case for deletion of purchases"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, purchase_id: int, user_id: int) -> None:
        """
        Delete a purchase (purchases don't support soft delete currently)

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

            # For now, just validate - actual deletion would need repository method
            # TODO: Implement hard delete in repository
            raise NotImplementedError(
                "Purchase deletion is not yet implemented. "
                "Purchases don't currently support soft delete."
            )
