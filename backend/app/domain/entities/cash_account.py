from dataclasses import dataclass
from typing import Optional

from app.domain.value_objects.money import Currency


@dataclass(frozen=True)
class CashAccount:
    """
    Domain entity representing a cash account.

    Invariants:
    - name must not be empty or only whitespace
    - name length must be between 1-100 characters
    - id can be None (before persistence)
    """

    id: Optional[int]
    payment_method_id: int
    user_id: int
    name: str
    currency: Currency

    def __post_init__(self):
        """Validate invariants after initialization"""
        # Validate name is not empty
        if not self.name or not self.name.strip():
            raise ValueError("Cash account name cannot be empty")

        # Normalize whitespace
        stripped_name = self.name.strip()
        if stripped_name != self.name:
            object.__setattr__(self, "name", stripped_name)

        # Validate name length
        if len(self.name) > 100:
            raise ValueError("Cash account name cannot exceed 100 characters")

        # Validate currency
        if not isinstance(self.currency, Currency):
            raise ValueError("Currency must be a valid Currency enum value")

    def __eq__(self, other):
        """CashAccounts are equal if they have the same ID"""
        if not isinstance(other, CashAccount):
            return False
        if self.id is None and other.id is None:
            return self is other
        return self.id == other.id

    def __hash__(self):
        """Allow CashAccount to be used in sets/dicts"""
        return hash(self.id) if self.id is not None else id(self)
