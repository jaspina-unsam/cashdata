from dataclasses import dataclass
from datetime import date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

from app.domain.value_objects.money import Money


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
            raise ValueError(
                f"billing_close_day must be between 1-31, got {self.billing_close_day}"
            )

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

        The billing period represents the statement month when the purchase
        will appear, not the charge month. This matches real-world credit
        card statement labeling.

        Logic:
        - If purchase day <= closure day: current statement (same month)
        - If purchase day > closure day: next statement (next month)

        Example:
        - Card closes on day 10
        - Purchase on Jan 5 (before close) → Jan 10 statement → Period "202501"
        - Purchase on Jan 15 (after close) → Feb 10 statement → Period "202502"
        
        Real example:
        - Close day 30, Purchase Nov 26 → Nov 30 statement → Period "202511"
        """
        if purchase_date.day <= self.billing_close_day:
            # Purchase before closure → current month statement
            period_date = purchase_date
        else:
            # Purchase after closure → next month statement
            period_date = purchase_date + relativedelta(months=1)

        return period_date.strftime("%Y%m")

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
