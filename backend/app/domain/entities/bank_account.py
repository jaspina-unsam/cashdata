from dataclasses import dataclass
from typing import Optional

from app.domain.exceptions.domain_exceptions import (
    BankAccountNameError,
    BankAccountUserError,
)
from app.domain.value_objects.money import Currency


@dataclass(frozen=True)
class BankAccount:
    """
    Domain entity representing a bank account.

    Invariants:
    - name must not be empty or only whitespace
    - name length must be between 1-100 characters
    - id can be None (before persistence)
    - primary_user_id and secondary_user_id cannot be the same
    """

    id: Optional[int]
    payment_method_id: int
    primary_user_id: int
    secondary_user_id: Optional[int]
    name: str
    bank: str
    account_type: str
    last_four_digits: str
    currency: Currency

    def __post_init__(self):
        """Validate invariants after initialization"""
        # Validate name is not empty
        if not self.name or not self.name.strip():
            raise BankAccountNameError("Bank account name cannot be empty")

        # Normalize whitespace
        stripped_name = self.name.strip()
        if stripped_name != self.name:
            object.__setattr__(self, "name", stripped_name)

        # Validate name length
        if len(self.name) > 100:
            raise BankAccountNameError("Bank account name cannot exceed 100 characters")

        # Validate primary user is not the same as secondary user
        if (
            self.secondary_user_id is not None
            and self.primary_user_id == self.secondary_user_id
        ):
            raise BankAccountUserError("Primary and secondary user cannot be the same")

        # Validate currency
        if not isinstance(self.currency, Currency):
            object.__setattr__(self, "currency", Currency(self.currency))

    def has_access(self, user_id: int) -> bool:
        """Check if the given user has access to this bank account"""
        return user_id == self.primary_user_id or user_id == self.secondary_user_id

    def __eq__(self, other):
        """BankAccounts are equal if they have the same ID"""
        if not isinstance(other, BankAccount):
            return False
        if self.id is None and other.id is None:
            return self is other
        return self.id == other.id

    def __hash__(self):
        """Allow BankAccount to be used in sets/dicts"""
        return hash(self.id) if self.id is not None else id(self)
