from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.budget_participant import BudgetParticipant


class IBudgetParticipantRepository(ABC):
    @abstractmethod
    def find_by_id(self, participant_id: int) -> Optional[BudgetParticipant]:
        """Retrieve budget participant by ID"""
        pass

    @abstractmethod
    def find_by_budget_id(self, budget_id: int) -> List[BudgetParticipant]:
        """Find all participants for a specific budget"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[BudgetParticipant]:
        """Find all budgets where a user is a participant"""
        pass

    @abstractmethod
    def find_by_budget_and_user(self, budget_id: int, user_id: int) -> Optional[BudgetParticipant]:
        """Find a specific participant relationship"""
        pass

    @abstractmethod
    def save(self, participant: BudgetParticipant) -> BudgetParticipant:
        """Insert or update budget participant"""
        pass

    @abstractmethod
    def save_many(self, participants: List[BudgetParticipant]) -> List[BudgetParticipant]:
        """Insert or update multiple budget participants"""
        pass

    @abstractmethod
    def delete(self, participant_id: int) -> None:
        """Delete budget participant by ID"""
        pass

    @abstractmethod
    def delete_by_budget_id(self, budget_id: int) -> None:
        """Delete all participants for a specific budget"""
        pass

    @abstractmethod
    def delete_by_budget_and_user(self, budget_id: int, user_id: int) -> None:
        """Delete a specific participant relationship"""
        pass