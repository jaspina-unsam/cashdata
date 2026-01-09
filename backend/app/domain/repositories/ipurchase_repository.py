from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.purchase import Purchase


class IPurchaseRepository(ABC):
    @abstractmethod
    def find_by_id(self, purchase_id: int) -> Optional[Purchase]:
        """Retrieve purchase by ID"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[Purchase]:
        """Retrieve all purchases for a specific user"""
        pass

    @abstractmethod
    def find_by_credit_card_id(self, card_id: int) -> List[Purchase]:
        """Retrieve all purchases for a specific credit card"""
        pass

    @abstractmethod
    def save(self, purchase: Purchase) -> Purchase:
        """Insert or update purchase"""
        pass

    @abstractmethod
    def delete(self, purchase_id: int) -> None:
        """Delete purchase by ID"""
        pass
