from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from cashdata.domain.exceptions.domain_exceptions import InvalidEntity
from cashdata.domain.value_objects.money import Money


@dataclass
class User:
    """
    Generates a system user using an id-based entity.

    Attributes:
        id: Unique identifier
        name: Of the user
        email: to send reminders and reports
        wage: montly income
    """

    id: Optional[int]
    name: str
    email: str
    wage: Money
    is_deleted: bool = False
    deleted_at: datetime | None = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise InvalidEntity("Name cannot be empty")

        if not self.email or "@" not in self.email:
            raise InvalidEntity("Invalid email format")

        if self.wage < Money(0, self.wage.currency):
            raise InvalidEntity("Wage must be positive")

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: "User") -> bool:
        if not isinstance(other, User):
            return False

        return self.id == other.id

    def __str__(self) -> str:
        return f"User({self.name}, {self.email})"

    def update_wage(self, new_wage: Money) -> None:
        """
        Updates the wage of the user
        """
        if new_wage <= Money("0", new_wage.currency):
            raise InvalidEntity("Wage must be positive")

        self.wage = new_wage

    def update_name(self, new_name: str) -> None:
        """
        Updates the name of the user
        """

        self.name = str(new_name)

    def update_email(self, new_email: str) -> None:
        """
        Updates the email of the user
        """
        if not self.email or "@" not in self.email:
            raise InvalidEntity("Invalid email format")

        self.email = new_email

    def mark_as_deleted(self) -> None:
        """Soft delete"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
