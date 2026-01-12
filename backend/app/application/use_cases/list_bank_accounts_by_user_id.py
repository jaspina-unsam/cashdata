from typing import Optional
from app.application.mappers.bank_account_mapper import BankAccountDTOMapper
from app.domain.repositories.iunit_of_work import IUnitOfWork


class ListBankAccountsUseCase:
    """
    Use case to list all bank accounts
    Usage options:
    - If user_id is provided, lists bank accounts for that user, either if they are primary or secondary
    - If no user_id is provided, lists all bank accounts in the system

    Validations:
    That the user exists if user_id is provided
    """

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, user_id: Optional[int] = None) -> list:
        """
        Execute the use case to list bank accounts.

        Args:
            user_id: Optional user ID to filter bank accounts
        Returns:
            List of BankAccount entities
        """
        with self._uow as uow:
            if user_id is not None:
                if not uow.users.exists_by_id(user_id):
                    raise ValueError("User does not exist.")

                bank_accounts = uow.bank_accounts.find_by_user_id(user_id)
            else:
                bank_accounts = uow.bank_accounts.find_all()

            return [BankAccountDTOMapper.to_response_dto(ba) for ba in bank_accounts]
