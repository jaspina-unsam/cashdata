"""Unit tests for MonthlyStatement entity."""

import pytest
from datetime import date

from cashdata.domain.entities.monthly_statement import MonthlyStatement
from cashdata.domain.exceptions.domain_exceptions import InvalidStatementDateRange


class TestMonthlyStatementValidation:
    """Test validation rules in MonthlyStatement entity."""

    def test_valid_statement_creation(self):
        """Test creating a valid monthly statement."""
        statement = MonthlyStatement(
            id=None,
            credit_card_id=1,
            start_date=date(2023, 12, 8),
            closing_date=date(2024, 1, 7),
            due_date=date(2024, 1, 27),
        )

        assert statement.credit_card_id == 1
        assert statement.start_date == date(2023, 12, 8)
        assert statement.closing_date == date(2024, 1, 7)
        assert statement.due_date == date(2024, 1, 27)

    def test_closing_date_equals_due_date(self):
        """Test that close date can equal due date (same day payment)."""
        statement = MonthlyStatement(
            id=None,
            credit_card_id=1,
            start_date=date(2023, 12, 16),
            closing_date=date(2024, 1, 15),
            due_date=date(2024, 1, 15),
        )

        assert statement.closing_date == statement.due_date

    def test_closing_date_after_due_date_raises_error(self):
        """Test that close date after due date raises ValueError."""
        with pytest.raises(InvalidStatementDateRange) as err_desc:
            MonthlyStatement(
                id=None,
                credit_card_id=1,
                start_date=date(2023, 12, 28),
                closing_date=date(2024, 1, 27),
                due_date=date(2024, 1, 7),
            )

        assert "dates must satisfy" in str(err_desc).lower()

    def test_start_date_after_closing_date_raises_error(self):
        """Test that close date after due date raises ValueError."""
        with pytest.raises(InvalidStatementDateRange) as err_desc:
            MonthlyStatement(
                id=None,
                credit_card_id=1,
                start_date=date(2024, 2, 28),
                closing_date=date(2024, 1, 27),
                due_date=date(2024, 2, 10),
            )

        assert "dates must satisfy" in str(err_desc).lower()

    def test_statement_validates_start_before_closing(self):
        """start_date must be before closing_date."""
        with pytest.raises(InvalidStatementDateRange, match="start < closing"):
            MonthlyStatement(
                id=None,
                credit_card_id=1,
                start_date=date(2025, 9, 30),
                closing_date=date(2025, 9, 30),
                due_date=date(2025, 10, 20),
            )

    def test_includes_purchase_date(self):
        """Purchase within period is included."""
        stmt = MonthlyStatement(
            id=1,
            credit_card_id=1,
            start_date=date(2025, 8, 28),
            closing_date=date(2025, 10, 2),
            due_date=date(2025, 10, 20),
        )

        assert stmt.includes_purchase_date(date(2025, 9, 1))
        assert stmt.includes_purchase_date(date(2025, 10, 1))
        assert not stmt.includes_purchase_date(date(2025, 8, 27))
        assert not stmt.includes_purchase_date(date(2025, 10, 3))


class TestPurchaseDateInclusion:
    """Test purchase date inclusion logic."""

    def test_purchase_on_close_date_is_included(self):
        """Test purchase on billing close date is included in period."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            start_date=date(2024, 4, 7),
            closing_date=date(2024, 5, 7),
            due_date=date(2024, 5, 27),
        )

        purchase_date = date(2024, 5, 7)

        assert statement.includes_purchase_date(purchase_date) is True

    def test_purchase_on_period_start_is_included(self):
        """Test purchase on period start date is included."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            start_date=date(2024, 4, 8),
            closing_date=date(2024, 5, 7),
            due_date=date(2024, 5, 27),
        )

        purchase_date = date(2024, 4, 8)

        assert statement.includes_purchase_date(purchase_date) is True

    def test_purchase_in_middle_of_period_is_included(self):
        """Test purchase in middle of period is included."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            start_date=date(2024, 4, 8),
            closing_date=date(2024, 5, 7),
            due_date=date(2024, 5, 27),
        )

        purchase_date = date(2024, 4, 25)

        assert statement.includes_purchase_date(purchase_date) is True

    def test_purchase_before_period_is_excluded(self):
        """Test purchase before period start is excluded."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            start_date=date(2024, 4, 8),
            closing_date=date(2024, 5, 7),
            due_date=date(2024, 5, 27),
        )

        purchase_date = date(2024, 4, 7)

        assert statement.includes_purchase_date(purchase_date) is False

    def test_purchase_after_close_date_is_excluded(self):
        """Test purchase after billing close date is excluded."""
        statement = MonthlyStatement(
            id=1,
            credit_card_id=1,
            start_date=date(2024, 4, 8),
            closing_date=date(2024, 5, 7),
            due_date=date(2024, 5, 27),
        )

        purchase_date = date(2024, 5, 8)

        assert statement.includes_purchase_date(purchase_date) is False


class TestEqualityAndHash:
    """Test equality and hash methods for collections."""

    def test_statements_with_same_id_are_equal(self):
        """Test statements with same ID are considered equal."""
        statement1 = MonthlyStatement(
            id=1,
            credit_card_id=1,
            start_date=date(2024, 4, 8),
            closing_date=date(2024, 5, 7),
            due_date=date(2024, 5, 27),
        )
        statement2 = MonthlyStatement(
            id=1,
            credit_card_id=2,
            start_date=date(2024, 5, 8),
            closing_date=date(2024, 6, 7),
            due_date=date(2024, 6, 27),
        )

        assert statement1 == statement2

    def test_statements_with_different_ids_are_not_equal(self):
        """Test statements with different IDs are not equal."""
        statement1 = MonthlyStatement(
            id=1,
            credit_card_id=1,
            start_date=date(2024, 4, 8),
            closing_date=date(2024, 5, 7),
            due_date=date(2024, 5, 27),
        )
        statement2 = MonthlyStatement(
            id=2,
            credit_card_id=1,
            start_date=date(2024, 4, 8),
            closing_date=date(2024, 5, 7),
            due_date=date(2024, 5, 27),
        )

        assert statement1 != statement2

    def test_statements_can_be_used_in_set(self):
        """Test statements can be used in sets (hashable)."""
        statement1 = MonthlyStatement(
            id=1,
            credit_card_id=1,
            start_date=date(2024, 4, 8),
            closing_date=date(2024, 5, 7),
            due_date=date(2024, 5, 27),
        )
        statement2 = MonthlyStatement(
            id=2,
            credit_card_id=1,
            start_date=date(2024, 5, 8),
            closing_date=date(2024, 6, 7),
            due_date=date(2024, 6, 27),
        )

        statement_set = {statement1, statement2}
        assert len(statement_set) == 2
        assert statement1 in statement_set
        assert statement2 in statement_set


class TestStatementRepresentation:
    """Test string and number (duration) representations of a monthly statement."""

    def test_should_return_period_identifier(self):
        stmt = MonthlyStatement(
            id=None,
            credit_card_id=1,
            start_date=date(2025, 9, 15),
            closing_date=date(2025, 10, 15),
            due_date=date(2025, 10, 25),
        )

        assert stmt.get_period_identifier() == "202510"

    def test_should_return_period_display(self):
        stmt = MonthlyStatement(
            id=None,
            credit_card_id=1,
            start_date=date(2025, 9, 15),
            closing_date=date(2025, 10, 15),
            due_date=date(2025, 10, 25),
        )

        assert stmt.get_period_display() == "Sep 15 - Oct 15, 2025"

    def test_should_return_period_duration(self):
        stmt = MonthlyStatement(
            id=None,
            credit_card_id=1,
            start_date=date(2025, 9, 15),
            closing_date=date(2025, 10, 15),
            due_date=date(2025, 10, 25),
        )

        assert stmt.get_duration_days() == 31
