from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.cash_account import CashAccount


class ICashAccountRepository(ABC):
    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[CashAccount]:
        """Retrieve all cash accounts for a specific user"""
        pass

    @abstractmethod
    def find_by_id(self, account_id: int) -> CashAccount | None:
        """Retrieve cash account by ID"""
        pass

    @abstractmethod
    def save(self, cash_account: CashAccount) -> CashAccount:
        """Insert or update cash account"""
        pass

    @abstractmethod
    def delete(self, cash_account: CashAccount) -> None:
        """Delete cash account"""
        pass

    @abstractmethod
    def exists_by_payment_method_id(self, payment_method_id: int) -> bool:
        """Check if a cash account exists for the given payment method ID"""
        pass
