from calendar import monthrange
from datetime import date

from app.domain.entities.credit_card import CreditCard


class BillingPeriodCalculator:
    @staticmethod
    def calculate_closing_date(credit_card: CreditCard, billing_period: str) -> date:
        # Parse the billing period
        year = int(billing_period[:4])
        month = int(billing_period[4:6])

        # Calculate the exact dates for this statement
        _, last_day_of_month = monthrange(year, month)
        actual_close_day = min(credit_card.billing_close_day, last_day_of_month)

        return date(year, month, actual_close_day)

    @staticmethod
    def calculate_due_date(credit_card: CreditCard, closing_date: date) -> date:
        # Payment due date calculation
        if credit_card.payment_due_day >= credit_card.billing_close_day:
            # Due date is in the same month as close date
            _, last_day_of_due_month = monthrange(closing_date.year, closing_date.month)
            actual_due_day = min(credit_card.payment_due_day, last_day_of_due_month)
            due_date = date(closing_date.year, closing_date.month, actual_due_day)
        else:
            # Due day is before close day -> due date is next month
            next_month = closing_date.month + 1
            next_year = closing_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            _, last_day_of_payment_month = monthrange(next_year, next_month)
            actual_payment_day = min(
                credit_card.payment_due_day, last_day_of_payment_month
            )
            due_date = date(next_year, next_month, actual_payment_day)

        return due_date
