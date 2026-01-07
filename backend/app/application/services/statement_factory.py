"""Helper for automatic statement creation."""

from datetime import timedelta

from app.domain.entities.credit_card import CreditCard
from app.domain.entities.monthly_statement import MonthlyStatement
from app.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)
from app.domain.services.billing_period_calculator import BillingPeriodCalculator


class StatementFactory:

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
        closing_date = BillingPeriodCalculator.calculate_closing_date(
            credit_card, billing_period
        )

        due_date = BillingPeriodCalculator.calculate_due_date(credit_card, closing_date)

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
