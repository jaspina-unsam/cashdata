from dataclasses import dataclass
from datetime import date


@dataclass
class MonthlyStatement:
    """
    Domain entity representing a credit card monthly statement (resumen mensual).

    Each statement represents a billing period for a credit card, with specific
    closing and due dates. These dates can be customized per statement, overriding
    the credit card's default dates.

    Invariants:
    - billing_close_date must be before or equal to payment_due_date
    - id can be None (before persistence)
    """

    id: int | None
    credit_card_id: int
    billing_close_date: date  # Fecha de cierre específica de este resumen
    payment_due_date: date  # Fecha de vencimiento específica de este resumen

    def __post_init__(self):
        """Validate invariants after initialization"""
        # Validate dates relationship
        if self.billing_close_date > self.payment_due_date:
            raise ValueError(
                f"billing_close_date ({self.billing_close_date}) must be before "
                f"or equal to payment_due_date ({self.payment_due_date})"
            )

    def get_period_start_date(self, previous_close_date: date | None) -> date:
        """
        Calculate the start date of this statement's billing period.

        The period starts the day after the previous statement's close date.
        If there's no previous statement, we use a default lookback period.

        Args:
            previous_close_date: The closing date of the previous statement, or None

        Returns:
            The first day of this statement's billing period
        """
        if previous_close_date is None:
            # If no previous close date, period starts 30 days before this close
            from datetime import timedelta

            return self.billing_close_date - timedelta(days=30)

        from datetime import timedelta

        return previous_close_date + timedelta(days=1)

    def includes_purchase_date(
        self, purchase_date: date, previous_close_date: date | None
    ) -> bool:
        """
        Check if a purchase date falls within this statement's billing period.

        Args:
            purchase_date: The date of the purchase
            previous_close_date: The closing date of the previous statement

        Returns:
            True if the purchase belongs to this statement's period
        """
        period_start = self.get_period_start_date(previous_close_date)
        return period_start <= purchase_date <= self.billing_close_date

    def __eq__(self, other):
        """Statements are equal if they have the same ID"""
        if not isinstance(other, MonthlyStatement):
            return False
        if self.id is None and other.id is None:
            return self is other
        return self.id == other.id

    def __hash__(self):
        """Allow MonthlyStatement to be used in sets/dicts"""
        return hash(self.id) if self.id is not None else id(self)
