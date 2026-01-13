from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.payment_method_type import PaymentMethodType


class IPaymentMethodRepository(ABC):
    @abstractmethod
    def find_by_id(self, payment_method_id: int) -> Optional[PaymentMethod]:
        pass

    @abstractmethod
    def find_all(self) -> List[PaymentMethod]:
        """Find all payment methods from all users"""
        pass

    @abstractmethod
    def find_by_user_id(
        self, user_id: int, type: Optional[PaymentMethodType] = None
    ) -> List[PaymentMethod]:
        pass

    @abstractmethod
    def save(self, payment_method: PaymentMethod) -> PaymentMethod:
        pass

    @abstractmethod
    def delete(self, payment_method_id: int) -> None:
        pass
