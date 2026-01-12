from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.monthly_budget import MonthlyBudget


class IMonthlyBudgetRepository(ABC):
    @abstractmethod
    def find_by_id(self, budget_id: int) -> Optional[MonthlyBudget]:
        """Retrieve monthly budget by ID"""
        pass

    @abstractmethod
    def find_by_period_and_creator(self, period: str, created_by_user_id: int) -> Optional[MonthlyBudget]:
        """Find budget by period and creator"""
        pass

    @abstractmethod
    def find_by_period(self, period: str) -> List[MonthlyBudget]:
        """Find all budgets for a specific period"""
        pass

    @abstractmethod
    def find_by_user_participant(self, user_id: int) -> List[MonthlyBudget]:
        """Find all budgets where user is a participant"""
        pass

    @abstractmethod
    def save(self, budget: MonthlyBudget) -> MonthlyBudget:
        """Insert or update monthly budget"""
        pass

    @abstractmethod
    def delete(self, budget_id: int) -> None:
        """Delete monthly budget by ID"""
        pass