from typing import List
from app.application.dtos.cash_account_dto import CashAccountResponseDTO
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.application.mappers.cash_account_mapper import CashAccountDTOMapper


class ListAllCashAccountsUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self) -> List[CashAccountResponseDTO]:
        """
        Retrieves all cash accounts from DB

        Returns:
            List[CashAccountResponseDTO]
        """
        with self._uow as uow:
            cash_accounts = uow.cash_accounts.find_all()
            return [CashAccountDTOMapper.to_response_dto(ca) for ca in cash_accounts]
