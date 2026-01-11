from typing import List
from app.application.dtos.cash_account_dto import CashAccountResponseDTO
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.application.mappers.cash_account_mapper import CashAccountDTOMapper


class ListCashAccountsByUserIdUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, user_id: int) -> List[CashAccountResponseDTO]:
        """
        Retrieves all cash accounts owned by the user from DB

        Returns:
            List[CashAccountResponseDTO]
        """
        with self._uow as uow:
            cash_accounts = uow.cash_accounts.find_by_user_id(user_id)
            return [CashAccountDTOMapper.to_response_dto(ca) for ca in cash_accounts]
