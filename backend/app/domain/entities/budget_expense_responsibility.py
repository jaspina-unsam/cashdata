from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.domain.exceptions.domain_exceptions import InvalidEntity
from app.domain.value_objects.money import Money


@dataclass(frozen=True)
class BudgetExpenseResponsibility:
    """
    Domain entity representing a user's responsibility for a budget expense.

    Invariants:
    - percentage must be between 0 and 100 (inclusive)
    - responsible_amount must be >= 0
    - user_id and budget_expense_id must be positive
    - id can be None (before persistence)
    """

    id: Optional[int]
    budget_expense_id: int
    user_id: int
    percentage: Decimal
    responsible_amount: Money

    def __post_init__(self):
        """Validate invariants after initialization"""
        # Validate percentage range
        if not (Decimal("0") <= self.percentage <= Decimal("100")):
            raise InvalidEntity(f"Percentage must be between 0 and 100, got {self.percentage}")

        # Validate responsible_amount is not negative
        if self.responsible_amount < Money(0, self.responsible_amount.currency):
            raise InvalidEntity("Responsible amount cannot be negative")

        # Validate IDs are positive
        if self.budget_expense_id <= 0:
            raise InvalidEntity("budget_expense_id must be positive")
        if self.user_id <= 0:
            raise InvalidEntity("user_id must be positive")

    def __str__(self) -> str:
        return f"BudgetExpenseResponsibility(user_{self.user_id}, {self.percentage}%, {self.responsible_amount})"