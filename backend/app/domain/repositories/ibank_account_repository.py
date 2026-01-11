from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.bank_account import BankAccount


class IBankAccountRepository(ABC):
    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[BankAccount]:
        """Retrieve all bank accounts for a specific user"""
        pass

    @abstractmethod
    def find_by_id(self, account_id: int) -> BankAccount | None:
        """Retrieve bank account by ID"""
        pass

    @abstractmethod
    def save(self, bank_account: BankAccount) -> BankAccount:
        """Insert or update bank account"""
        pass

    @abstractmethod
    def delete(self, bank_account: BankAccount) -> None:
        """Delete bank account"""
        pass

    @abstractmethod
    def find_all(self) -> List[BankAccount]:
        """Retrieve all bank accounts"""
        pass