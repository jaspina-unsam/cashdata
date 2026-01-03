from abc import ABC, abstractmethod
from typing import List, Optional

from cashdata.domain.entities.credit_card import CreditCard


class ICreditCardRepository(ABC):
    @abstractmethod
    def find_by_id(self, card_id: int) -> Optional[CreditCard]:
        """Retrieve credit card by ID"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[CreditCard]:
        """Retrieve all credit cards for a specific user"""
        pass

    @abstractmethod
    def save(self, card: CreditCard) -> CreditCard:
        """Insert or update credit card"""
        pass
