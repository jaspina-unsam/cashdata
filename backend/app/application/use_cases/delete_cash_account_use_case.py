from app.domain.repositories.iunit_of_work import IUnitOfWork


class DeleteCashAccountUseCase:
    """Use case for hard deletion of cash accounts"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, cash_account_id: int) -> None:
        """
        Hard delete a cash account

        Args:
            cash_account_id: ID of the cash account to delete

        Raises:
            ValueError: If cash account doesn't exist
        """

        with self._uow as uow:
            cash_account = uow.cash_accounts.find_by_id(cash_account_id)
            if cash_account is None:
                raise ValueError(
                    f"Cash account with ID {cash_account_id} not found"
                )

            uow.cash_accounts.delete(cash_account)
            uow.commit()
