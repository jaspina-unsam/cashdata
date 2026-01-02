"""Helper for automatic statement creation."""

from datetime import date
from dateutil.relativedelta import relativedelta

from cashdata.domain.entities.tarjeta_credito import CreditCard
from cashdata.domain.entities.monthly_statement import MonthlyStatement
from cashdata.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)


def get_or_create_statement_for_date(
    credit_card: CreditCard,
    purchase_date: date,
    statement_repository: IMonthlyStatementRepository,
) -> MonthlyStatement:
    """Get or create a statement for the given purchase date.

    This function determines which statement period a purchase falls into
    and creates the statement if it doesn't exist yet.

    Args:
        credit_card: The credit card
        purchase_date: The purchase date
        statement_repository: Repository to check/create statements

    Returns:
        The statement for this period (existing or newly created)
    """
    # Determine which month's statement this purchase belongs to
    # If purchase is after the card's close day, it goes to next month's statement
    if purchase_date.day > credit_card.billing_close_day:
        # Purchase after close day -> next month's statement
        statement_month = purchase_date + relativedelta(months=1)
    else:
        # Purchase before/on close day -> current month's statement
        statement_month = purchase_date

    # Calculate the exact dates for this statement
    billing_close_date = date(
        statement_month.year, statement_month.month, credit_card.billing_close_day
    )

    # Payment due date is card's due day in the same month
    # (or next month if due day < close day)
    if credit_card.payment_due_day >= credit_card.billing_close_day:
        payment_due_date = date(
            statement_month.year, statement_month.month, credit_card.payment_due_day
        )
    else:
        # Due day is before close day -> due date is next month
        payment_month = statement_month + relativedelta(months=1)
        payment_due_date = date(
            payment_month.year, payment_month.month, credit_card.payment_due_day
        )

    # Check if a statement already exists for this period
    # Look for statements with the same billing_close_date for this card
    existing_statements = statement_repository.find_by_credit_card_id(
        credit_card.id, include_future=True
    )

    for stmt in existing_statements:
        if stmt.billing_close_date == billing_close_date:
            return stmt

    # No statement found, create one
    new_statement = MonthlyStatement(
        id=None,
        credit_card_id=credit_card.id,
        billing_close_date=billing_close_date,
        payment_due_date=payment_due_date,
    )

    return statement_repository.save(new_statement)
