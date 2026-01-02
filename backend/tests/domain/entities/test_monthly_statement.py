"""Unit tests for MonthlyStatement entity."""

import pytest
from datetime import date, timedelta

from cashdata.domain.entities.monthly_statement import MonthlyStatement


class TestMonthlyStatementValidation:
    """Test validation rules in MonthlyStatement entity."""

    def test_valid_statement_creation(self):
        """Test creating a valid monthly statement."""
        statement = MonthlyStatement(
            id=None,
            credit_card_id=1,
            billing_close_date=date(2024, 1, 7),
            payment_due_date=date(2024, 1, 27),
        )

        assert statement.credit_card_id == 1
        assert statement.billing_close_date == date(2024, 1, 7)
        assert statement.payment_due_date == date(2024, 1, 27)

    def test_billing_close_date_equals_payment_due_date(self):
        """Test that close date can equal due date (same day payment)."""
        statement = MonthlyStatement(
            id=None,
            credit_card_id=1,
            billing_close_date=date(2024, 1, 15),
            payment_due_date=date(2024, 1, 15),
        )

        assert statement.billing_close_date == statement.payment_due_date

    def test_billing_close_date_after_payment_due_date_raises_error(self):
        """Test that close date after due date raises ValueError."""
        with pytest.raises(
            ValueError,
            match="billing_close_date .* must be before or equal to payment_due_date",
        ):
            MonthlyStatement(
                id=None,
                credit_card_id=1,
                billing_close_date=date(2024, 1, 27),
                payment_due_date=date(2024, 1, 7),
            )


class TestPeriodStartCalculation:
    """Test period start date calculation logic."""

    def test_period_start_with_previous_close_date(self):
        """Test period starts the day after previous statement closes."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )

        previous_close = date(2024, 4, 8)
        period_start = statement.get_period_start_date(previous_close)

        # Period should start April 9 (day after previous close)
        assert period_start == date(2024, 4, 9)

    def test_period_start_without_previous_close_date(self):
        """Test period start defaults to 30 days before close when no previous."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )

        period_start = statement.get_period_start_date(None)

        # Period should start 30 days before close: May 7 - 30 days = April 7
        expected_start = date(2024, 5, 7) - timedelta(days=30)
        assert period_start == expected_start

    def test_period_start_first_day_of_month(self):
        """Test period start calculation when previous close is end of month."""
        statement = MonthlyStatement(
            id=2,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 31),
            payment_due_date=date(2024, 6, 20),
        )

        previous_close = date(2024, 4, 30)
        period_start = statement.get_period_start_date(previous_close)

        # Period should start May 1 (day after April 30)
        assert period_start == date(2024, 5, 1)


class TestPurchaseDateInclusion:
    """Test purchase date inclusion logic."""

    def test_purchase_on_close_date_is_included(self):
        """Test purchase on billing close date is included in period."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )

        previous_close = date(2024, 4, 8)
        purchase_date = date(2024, 5, 7)  # Same as close date

        assert statement.includes_purchase_date(purchase_date, previous_close) is True

    def test_purchase_on_period_start_is_included(self):
        """Test purchase on period start date is included."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )

        previous_close = date(2024, 4, 8)
        purchase_date = date(2024, 4, 9)  # Period start

        assert statement.includes_purchase_date(purchase_date, previous_close) is True

    def test_purchase_in_middle_of_period_is_included(self):
        """Test purchase in middle of period is included."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )

        previous_close = date(2024, 4, 8)
        purchase_date = date(2024, 4, 25)  # Between April 9 and May 7

        assert statement.includes_purchase_date(purchase_date, previous_close) is True

    def test_purchase_before_period_is_excluded(self):
        """Test purchase before period start is excluded."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )

        previous_close = date(2024, 4, 8)
        purchase_date = date(2024, 4, 8)  # On previous close (before period start)

        assert statement.includes_purchase_date(purchase_date, previous_close) is False

    def test_purchase_after_close_date_is_excluded(self):
        """Test purchase after billing close date is excluded."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )

        previous_close = date(2024, 4, 8)
        purchase_date = date(2024, 5, 8)  # Day after close

        assert statement.includes_purchase_date(purchase_date, previous_close) is False

    def test_purchase_inclusion_without_previous_close(self):
        """Test purchase inclusion when there's no previous statement."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )

        # Period starts 30 days before close: April 7
        purchase_date = date(2024, 4, 10)

        assert statement.includes_purchase_date(purchase_date, None) is True

    def test_purchase_before_30_day_window_is_excluded(self):
        """Test purchase before 30-day lookback window is excluded."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )

        # Period starts April 7 (30 days before close)
        purchase_date = date(2024, 4, 6)  # Before 30-day window

        assert statement.includes_purchase_date(purchase_date, None) is False


class TestEqualityAndHash:
    """Test equality and hash methods for collections."""

    def test_statements_with_same_id_are_equal(self):
        """Test statements with same ID are considered equal."""
        statement1 = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )
        statement2 = MonthlyStatement(
            id=1,
            credit_card_id=2,  # Different card
            billing_close_date=date(2024, 6, 7),  # Different dates
            payment_due_date=date(2024, 6, 27),
        )

        assert statement1 == statement2

    def test_statements_with_different_ids_are_not_equal(self):
        """Test statements with different IDs are not equal."""
        statement1 = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )
        statement2 = MonthlyStatement(
            id=2,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )

        assert statement1 != statement2

    def test_statements_can_be_used_in_set(self):
        """Test statements can be used in sets (hashable)."""
        statement1 = MonthlyStatement(
            id=1,
            credit_card_id=1,
            billing_close_date=date(2024, 5, 7),
            payment_due_date=date(2024, 5, 27),
        )
        statement2 = MonthlyStatement(
            id=2,
            credit_card_id=1,
            billing_close_date=date(2024, 6, 7),
            payment_due_date=date(2024, 6, 27),
        )

        statement_set = {statement1, statement2}
        assert len(statement_set) == 2
        assert statement1 in statement_set
        assert statement2 in statement_set
