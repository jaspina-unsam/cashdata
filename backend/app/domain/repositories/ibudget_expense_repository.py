from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.budget_expense import BudgetExpense


class IBudgetExpenseRepository(ABC):
    @abstractmethod
    def find_by_id(self, expense_id: int) -> Optional[BudgetExpense]:
        """Retrieve budget expense by ID"""
        pass

    @abstractmethod
    def find_by_budget_id(self, budget_id: int) -> List[BudgetExpense]:
        """Find all expenses for a specific budget"""
        pass

    @abstractmethod
    def find_by_purchase_id(self, purchase_id: int) -> List[BudgetExpense]:
        """Find all expenses associated with a specific purchase"""
        pass

    @abstractmethod
    def find_by_installment_id(self, installment_id: int) -> List[BudgetExpense]:
        """Find all expenses associated with a specific installment"""
        pass

    @abstractmethod
    def find_by_paid_by_user_id(self, user_id: int) -> List[BudgetExpense]:
        """Find all expenses paid by a specific user"""
        pass

    @abstractmethod
    def save(self, expense: BudgetExpense) -> BudgetExpense:
        """Insert or update budget expense"""
        pass

    @abstractmethod
    def delete(self, expense_id: int) -> None:
        """Delete budget expense by ID"""
        pass