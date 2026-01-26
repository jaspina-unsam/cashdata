from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.domain.exceptions.domain_exceptions import InvalidEntity
from app.domain.value_objects.money import Money
from app.domain.value_objects.split_type import SplitType


@dataclass(frozen=True)
class BudgetExpense:
    """
    Domain entity representing an expense within a budget.

    Invariants:
    - Exactly one of purchase_id or installment_id must be set (XOR constraint)
    - amount must be positive
    - description must not be empty if provided
    - date must be valid
    - split_type must be valid SplitType
    - id can be None (before persistence)
    """

    id: Optional[int]
    budget_id: int
    purchase_id: Optional[int]
    installment_id: Optional[int]
    paid_by_user_id: int
    split_type: SplitType
    amount: Money
    currency: str
    description: Optional[str]
    date: date
    payment_method_name: Optional[str]
    created_at: date # type: ignore

    def __post_init__(self):
        """Validate invariants after initialization"""
        # Validate XOR constraint: exactly one of purchase_id or installment_id must be set
        has_purchase = self.purchase_id is not None
        has_installment = self.installment_id is not None

        if not (has_purchase ^ has_installment):  # XOR: one and only one must be True
            raise InvalidEntity(
                "Exactly one of purchase_id or installment_id must be set, but not both"
            )

        # Validate description if provided
        if self.description is not None and not self.description.strip():
            raise InvalidEntity("Description cannot be empty string if provided")

        # Validate split_type
        if not isinstance(self.split_type, SplitType):
            raise InvalidEntity("split_type must be a valid SplitType")

        # Validate budget_id and paid_by_user_id are positive
        if self.budget_id <= 0:
            raise InvalidEntity("budget_id must be positive")
        if self.paid_by_user_id <= 0:
            raise InvalidEntity("paid_by_user_id must be positive")

    def __str__(self) -> str:
        return f"{self.description} - {self.amount} - paid_by_user_{self.paid_by_user_id}"

    def is_from_purchase(self) -> bool:
        """Check if this expense comes from a purchase"""
        return self.purchase_id is not None

    def is_from_installment(self) -> bool:
        """Check if this expense comes from an installment"""
        return self.installment_id is not None

    def get_reference_id(self) -> int:
        """Get the purchase_id or installment_id (whichever is set)"""
        return self.purchase_id if self.purchase_id is not None else self.installment_id