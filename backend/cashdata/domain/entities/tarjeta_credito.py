from dataclasses import dataclass
from datetime import date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

from cashdata.domain.value_objects.money import Money


@dataclass(frozen=True)
class CreditCard:
    """
    Domain entity representing a credit card.

    Invariants:
    - dia_cierre must be between 1-31
    - dia_vencimiento must be between 1-31
    - ultimos_4_digitos must be exactly 4 numeric characters
    - nombre cannot be empty

    Business Logic:
    - Calculates billing period based on purchase date and closure day
    """

    id: int | None
    user_id: int
    name: str
    bank: str
    last_four_digits: str
    billing_close_day: int
    payment_due_day: int
    credit_limit: Money | None = None

    def __post_init__(self):
        """Validate invariants"""
        # Validate name is not empty
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")

        # Validate billing_close_day
        if not (1 <= self.billing_close_day <= 31):
            raise ValueError(f"billing_close_day must be between 1-31, got {self.billing_close_day}")

        # Validate payment_due_day
        if not (1 <= self.payment_due_day <= 31):
            raise ValueError(
                f"payment_due_day must be between 1-31, got {self.payment_due_day}"
            )

        # Validate last_four_digits
        if len(self.last_four_digits) != 4:
            raise ValueError("last_four_digits must be exactly 4 characters")

        if not self.last_four_digits.isdigit():
            raise ValueError("last_four_digits must contain only digits")

    def calculate_billing_period(self, purchase_date: date) -> str:
        """
        Calculate billing period (YYYYMM) for a purchase date.

        Logic:
        - If purchase day <= closure day: current month
        - If purchase day > closure day: next month

        Example:
        - Card closes on day 10
        - Purchase on Jan 5 → Period "202501"
        - Purchase on Jan 15 → Period "202502"
        """
        if purchase_date.day <= self.billing_close_day:
            # Purchase before closure → current period
            period_date = purchase_date
        else:
            # Purchase after closure → next period
            period_date = purchase_date + relativedelta(months=1)

        return period_date.strftime("%Y%m")

    def calculate_due_date(self, period: str) -> date:
        """
        Calculate due date for a billing period.

        Args:
            period: "YYYYMM" format

        Returns:
            Due date for that period

        Example:
        - Period "202501", due day 20 → 2025-01-20
        - Period "202501", due day 5, closure 25 → 2025-02-05 (next month)
        """
        # Parse "202501" → year=2025, month=1
        year = int(period[:4])
        month = int(period[4:6])

        # Create base date with due day
        try:
            due_date = date(year, month, self.payment_due_day)
        except ValueError:
            # Invalid day for month (e.g.: 31 in February)
            # Use last day of month
            last_day = monthrange(year, month)[1]
            due_date = date(year, month, last_day)

        # If due < closure, it's next month
        if self.payment_due_day < self.billing_close_day:
            due_date = due_date + relativedelta(months=1)

        return due_date

    def __eq__(self, other):
        """Credit cards are equal if they have the same ID"""
        if not isinstance(other, CreditCard):
            return False
        # If both are new (id=None), compare by reference
        if self.id is None and other.id is None:
            return self is other
        return self.id == other.id

    def __hash__(self):
        """Allow TarjetaCredito to be used in sets/dicts"""
        return hash(self.id) if self.id is not None else id(self)
