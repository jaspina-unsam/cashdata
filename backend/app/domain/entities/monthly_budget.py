from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.exceptions.domain_exceptions import InvalidEntity
from app.domain.value_objects.period import Period
from app.domain.value_objects.budget_status import BudgetStatus


@dataclass(frozen=True)
class MonthlyBudget:
    """
    Domain entity representing a monthly budget for expense sharing.

    Invariants:
    - name must not be empty or only whitespace
    - period must be valid
    - created_by_user_id must be positive
    - status must be valid BudgetStatus
    - id can be None (before persistence)
    """

    id: Optional[int]
    name: str
    period: Period
    description: Optional[str]
    status: BudgetStatus
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    def __post_init__(self):
        """Validate invariants after initialization"""
        # Validate name
        if not self.name or not self.name.strip():
            raise InvalidEntity("Budget name cannot be empty")

        # Validate created_by_user_id
        if self.created_by_user_id <= 0:
            raise InvalidEntity("created_by_user_id must be positive")

        # Validate status
        if not isinstance(self.status, BudgetStatus):
            raise InvalidEntity("status must be a valid BudgetStatus")

    def __str__(self) -> str:
        return f"MonthlyBudget({self.name}, Period(year={self.period.year}, month={self.period.month}), {self.status.value})"

    def is_active(self) -> bool:
        """Check if budget is in active status"""
        return self.status == BudgetStatus.ACTIVE

    def can_be_edited(self) -> bool:
        """Check if budget can be edited (only active budgets)"""
        return self.is_active()