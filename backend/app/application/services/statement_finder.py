"""Helper for automatic statement creation."""

from datetime import date, timedelta
from calendar import monthrange

from app.domain.entities.credit_card import CreditCard
from app.domain.entities.monthly_statement import MonthlyStatement
from app.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)


class StatementFinder:

    @staticmethod
    def get_or_create_statement_for_period(
        credit_card: CreditCard,
        billing_period: str,
        statement_repository: IMonthlyStatementRepository,
    ) -> MonthlyStatement:
        """Get or create a statement for the given billing period.

        Args:
            credit_card: The credit card
            billing_period: The billing period in YYYYMM format (e.g., "202508")
            statement_repository: Repository to check/create statements

        Returns:
            The statement for this period (existing or newly created)
        """
        # Parse the billing period
        year = int(billing_period[:4])
        month = int(billing_period[4:6])

        # Calculate the exact dates for this statement
        _, last_day_of_month = monthrange(year, month)
        actual_close_day = min(credit_card.billing_close_day, last_day_of_month)

        closing_date = date(year, month, actual_close_day)

        # Payment due date calculation
        if credit_card.payment_due_day >= credit_card.billing_close_day:
            # Due date is in the same month as close date
            _, last_day_of_due_month = monthrange(year, month)
            actual_due_day = min(credit_card.payment_due_day, last_day_of_due_month)
            due_date = date(year, month, actual_due_day)
        else:
            # Due day is before close day -> due date is next month
            next_month = month + 1
            next_year = year
            if next_month > 12:
                next_month = 1
                next_year += 1
            _, last_day_of_payment_month = monthrange(next_year, next_month)
            actual_payment_day = min(
                credit_card.payment_due_day, last_day_of_payment_month
            )
            due_date = date(next_year, next_month, actual_payment_day)

        # Check if a statement already exists for this period
        # Match by period identifier (uses start_date month)
        existing_statements = statement_repository.find_by_credit_card_id(
            credit_card.id, include_future=True
        )

        for stmt in existing_statements:
            # Use the entity's period identifier method
            if stmt.get_period_identifier() == billing_period:
                return stmt

        # No statement found, need to create one
        # Calculate start_date based on previous statement or estimate

        # Sort statements by closing date to find the most recent one before this
        sorted_statements = sorted(existing_statements, key=lambda s: s.closing_date)

        # Find previous statement (last one that closed before this one)
        previous_statement = None
        for stmt in sorted_statements:
            if stmt.closing_date < closing_date:
                previous_statement = stmt
            else:
                break

        if previous_statement:
            # Start date is day after previous statement closed
            start_date = previous_statement.closing_date + timedelta(days=1)
        else:
            # No previous statement - estimate based on typical billing cycle (30 days)
            start_date = closing_date - timedelta(days=30)

        # Create new statement
        new_statement = MonthlyStatement(
            id=None,
            credit_card_id=credit_card.id,
            start_date=start_date,
            closing_date=closing_date,
            due_date=due_date,
        )

        return statement_repository.save(new_statement)
