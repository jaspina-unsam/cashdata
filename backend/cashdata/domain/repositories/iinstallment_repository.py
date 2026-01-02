from abc import ABC, abstractmethod
from typing import List, Optional

from cashdata.domain.entities.installment import Installment


class IInstallmentRepository(ABC):
    @abstractmethod
    def find_by_id(self, installment_id: int) -> Optional[Installment]:
        """Retrieve installment by ID"""
        pass

    @abstractmethod
    def find_by_purchase_id(self, purchase_id: int) -> List[Installment]:
        """Retrieve all installments for a specific purchase"""
        pass

    @abstractmethod
    def find_by_billing_period(self, period: str) -> List[Installment]:
        """Retrieve all installments for a specific billing period (YYYYMM)"""
        pass

    @abstractmethod
    def find_by_credit_card_and_period(
        self, card_id: int, period: str
    ) -> List[Installment]:
        """Retrieve installments for a credit card in a specific period"""
        pass

    @abstractmethod
    def save(self, installment: Installment) -> Installment:
        """Insert or update installment"""
        pass

    @abstractmethod
    def save_all(self, installments: List[Installment]) -> List[Installment]:
        """Insert or update multiple installments (bulk operation)"""
        pass
