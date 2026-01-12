from dataclasses import dataclass
from typing import Optional

from app.domain.exceptions.domain_exceptions import InvalidEntity


@dataclass(frozen=True)
class BudgetParticipant:
    """
    Domain entity representing a user's participation in a monthly budget.

    This is a many-to-many relationship entity between MonthlyBudget and User.

    Invariants:
    - budget_id must be positive
    - user_id must be positive
    - id can be None (before persistence)
    """

    id: Optional[int]
    budget_id: int
    user_id: int

    def __post_init__(self):
        """Validate invariants after initialization"""
        # Validate budget_id
        if self.budget_id <= 0:
            raise InvalidEntity("budget_id must be positive")

        # Validate user_id
        if self.user_id <= 0:
            raise InvalidEntity("user_id must be positive")

    def __str__(self) -> str:
        return f"BudgetParticipant(budget_{self.budget_id}, user_{self.user_id})"