from dataclasses import dataclass
from datetime import date

from app.domain.value_objects.money import Money


@dataclass(frozen=True)
class Purchase:
    """
    Domain entity representing a credit card purchase or credit.

    Invariants:
    - installments_count must be >= 1
    - total_amount must be != 0 (negative for credits/bonifications, positive for purchases)
    - description must not be empty or only whitespace
    - id can be None (before persistence)
    """

    id: int | None
    user_id: int
    payment_method_id: int
    category_id: int
    purchase_date: date
    description: str
    total_amount: Money
    installments_count: int

    def __post_init__(self):
        """Validate invariants after initialization"""
        # Validate installments_count
        if self.installments_count < 1:
            raise ValueError(
                f"installments_count must be >= 1, got {self.installments_count}"
            )

        # Validate total_amount is not zero (can be negative for credits/bonifications)
        if self.total_amount.amount == 0:
            raise ValueError(
                f"total_amount cannot be zero, got {self.total_amount.amount}"
            )

        # Validate description is not empty
        if not self.description or not self.description.strip():
            raise ValueError("description cannot be empty")

        # Normalize whitespace in description
        stripped_description = self.description.strip()
        if stripped_description != self.description:
            object.__setattr__(self, "description", stripped_description)

    def __eq__(self, other):
        """Purchases are equal if they have the same ID"""
        if not isinstance(other, Purchase):
            return False
        if self.id is None and other.id is None:
            return self is other
        return self.id == other.id

    def __hash__(self):
        """Allow Purchase to be used in sets/dicts"""
        return hash(self.id) if self.id is not None else id(self)
