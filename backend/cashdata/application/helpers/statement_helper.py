"""Helper for automatic statement creation."""

from datetime import date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

from cashdata.domain.entities.credit_card import CreditCard
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
    # Handle months with fewer days than the billing_close_day
    # (e.g., close_day=30 but February has only 28 days)
    _, last_day_of_month = monthrange(statement_month.year, statement_month.month)
    actual_close_day = min(credit_card.billing_close_day, last_day_of_month)

    billing_close_date = date(
        statement_month.year, statement_month.month, actual_close_day
    )

    # Payment due date is card's due day in the same month
    # (or next month if due day < close day)
    if credit_card.payment_due_day >= credit_card.billing_close_day:
        # Due date is in the same month as close date
        _, last_day_of_due_month = monthrange(
            statement_month.year, statement_month.month
        )
        actual_due_day = min(credit_card.payment_due_day, last_day_of_due_month)
        payment_due_date = date(
            statement_month.year, statement_month.month, actual_due_day
        )
    else:
        # Due day is before close day -> due date is next month
        payment_month = statement_month + relativedelta(months=1)
        _, last_day_of_payment_month = monthrange(
            payment_month.year, payment_month.month
        )
        actual_payment_day = min(credit_card.payment_due_day, last_day_of_payment_month)
        payment_due_date = date(
            payment_month.year, payment_month.month, actual_payment_day
        )

    # Check if a statement already exists for this period
    # Search by period (year+month), not exact date, to avoid duplicates
    # when statement dates have been manually modified
    existing_statements = statement_repository.find_by_credit_card_id(
        credit_card.id, include_future=True
    )

    target_period = billing_close_date.strftime("%Y%m")
    for stmt in existing_statements:
        stmt_period = stmt.closing_date.strftime("%Y%m")
        if stmt_period == target_period:
            return stmt

    # No statement found, create one
    new_statement = MonthlyStatement(
        id=None,
        credit_card_id=credit_card.id,
        closing_date=billing_close_date,
        due_date=payment_due_date,
    )

    return statement_repository.save(new_statement)


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

    billing_close_date = date(year, month, actual_close_day)

    # Payment due date calculation
    if credit_card.payment_due_day >= credit_card.billing_close_day:
        # Due date is in the same month as close date
        _, last_day_of_due_month = monthrange(year, month)
        actual_due_day = min(credit_card.payment_due_day, last_day_of_due_month)
        payment_due_date = date(year, month, actual_due_day)
    else:
        # Due day is before close day -> due date is next month
        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month = 1
            next_year += 1
        _, last_day_of_payment_month = monthrange(next_year, next_month)
        actual_payment_day = min(credit_card.payment_due_day, last_day_of_payment_month)
        payment_due_date = date(next_year, next_month, actual_payment_day)

    # Check if a statement already exists for this period
    # Search by period (year+month), not exact date, to avoid duplicates
    # when statement dates have been manually modified
    existing_statements = statement_repository.find_by_credit_card_id(
        credit_card.id, include_future=True
    )

    for stmt in existing_statements:
        # Compare by period (YYYYMM) not exact date
        stmt_period = stmt.closing_date.strftime("%Y%m")
        target_period = billing_period
        if stmt_period == target_period:
            return stmt

    # No statement found, create one
    new_statement = MonthlyStatement(
        id=None,
        credit_card_id=credit_card.id,
        closing_date=billing_close_date,
        due_date=payment_due_date,
    )

    return statement_repository.save(new_statement)
