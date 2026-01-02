from cashdata.domain.repositories.iunit_of_work import IUnitOfWork


class DeleteCreditCardUseCase:
    """Use case for soft deletion of credit cards"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, credit_card_id: int, user_id: int) -> None:
        """
        Delete a credit card (not yet implemented - credit cards don't support soft delete)

        Args:
            credit_card_id: ID of the credit card to delete
            user_id: ID of the user who owns the card

        Raises:
            ValueError: If credit card doesn't exist or doesn't belong to user
            NotImplementedError: Credit card deletion not yet supported
        """
        with self._uow:
            credit_card = self._uow.credit_cards.find_by_id(credit_card_id)
            if credit_card is None or credit_card.user_id != user_id:
                raise ValueError(
                    f"Credit card with ID {credit_card_id} not found for user {user_id}"
                )

            # Credit cards don't support soft delete yet
            raise NotImplementedError(
                "Credit card deletion is not yet implemented. "
                "Credit cards don't currently support soft delete."
            )
