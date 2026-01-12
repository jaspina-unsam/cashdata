from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.domain.entities.budget_expense_responsibility import BudgetExpenseResponsibility


class IBudgetExpenseResponsibilityRepository(ABC):
    @abstractmethod
    def find_by_id(self, responsibility_id: int) -> Optional[BudgetExpenseResponsibility]:
        """Retrieve budget expense responsibility by ID"""
        pass

    @abstractmethod
    def find_by_budget_expense_id(self, budget_expense_id: int) -> List[BudgetExpenseResponsibility]:
        """Find all responsibilities for a specific budget expense"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[BudgetExpenseResponsibility]:
        """Find all responsibilities for a specific user"""
        pass

    @abstractmethod
    def find_by_budget_id(self, budget_id: int) -> Dict[int, List[BudgetExpenseResponsibility]]:
        """
        Find all responsibilities for a specific budget.
        Returns a dict where key is budget_expense_id and value is list of responsibilities.
        """
        pass

    @abstractmethod
    def save(self, responsibility: BudgetExpenseResponsibility) -> BudgetExpenseResponsibility:
        """Insert or update budget expense responsibility"""
        pass

    @abstractmethod
    def save_many(self, responsibilities: List[BudgetExpenseResponsibility]) -> List[BudgetExpenseResponsibility]:
        """Insert or update multiple budget expense responsibilities"""
        pass

    @abstractmethod
    def delete(self, responsibility_id: int) -> None:
        """Delete budget expense responsibility by ID"""
        pass

    @abstractmethod
    def delete_by_budget_expense_id(self, budget_expense_id: int) -> None:
        """Delete all responsibilities for a specific budget expense"""
        pass