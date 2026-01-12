from typing import List

from app.domain.entities.digital_wallet import DigitalWallet
from app.domain.repositories.iunit_of_work import IUnitOfWork


class ListDigitalWalletsByUserUseCase:
    """Use case to list all digital wallets for a user."""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, user_id: int) -> List[DigitalWallet]:
        with self._uow as uow:
            return uow.digital_wallets.find_by_user_id(user_id)
