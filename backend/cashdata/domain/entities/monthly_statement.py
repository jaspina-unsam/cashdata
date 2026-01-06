from dataclasses import dataclass
from datetime import date

from cashdata.domain.exceptions.domain_exceptions import InvalidStatementDateRange


@dataclass
class MonthlyStatement:
    """
    Credit card monthly statement with explicit period boundaries.

    Real-world example:
        start_date: 2025-08-28 (day after previous statement closed)
        closing_date: 2025-10-02 (actual closing date, even if in next month)
        due_date: 2025-10-20 (payment deadline)

    Invariants:
        start_date < closing_date <= due_date
    """

    id: int | None
    credit_card_id: int
    start_date: date
    closing_date: date
    due_date: date

    def __post_init__(self):
        """Validate invariants after initialization"""
        if not (self.start_date < self.closing_date <= self.due_date):
            raise InvalidStatementDateRange(
                f"Dates must satisfy: start < closing <= due. "
                f"Got: {self.start_date} < {self.closing_date} <= {self.due_date}"
            )

    def includes_purchase_date(self, purchase_date: date) -> bool:
        """
        Check if a purchase date falls within this statement's billing period.

        Args:
            purchase_date: The date of the purchase

        Returns:
            True if the purchase belongs to this statement's period
        """
        return self.start_date <= purchase_date <= self.closing_date

    def get_period_identifier(self) -> str:
        """
        Return period identifier (e.g. '202508' for August 2025).
        """
        return f"{self.closing_date.year}{self.closing_date.month:02d}"

    def get_period_display(self) -> str:
        """
        Return human-readable period matching bank statements.

        Example: 'Aug 28 - Oct 2, 2025'
        """

        start_str = self.start_date.strftime("%b %d")
        close_str = self.closing_date.strftime("%b %d, %Y")
        return f"{start_str} - {close_str}"

    def get_duration_days(self) -> int:
        """Return number of days in this period"""
        return (self.closing_date - self.start_date).days + 1

    def __eq__(self, other) -> bool:
        """Statements are equal if they have the same ID"""
        if not isinstance(other, MonthlyStatement):
            return False
        if self.id is None and other.id is None:
            return self is other
        return self.id == other.id

    def __hash__(self) -> int:
        """Allow MonthlyStatement to be used in sets/dicts"""
        return hash(self.id) if self.id is not None else id(self)
