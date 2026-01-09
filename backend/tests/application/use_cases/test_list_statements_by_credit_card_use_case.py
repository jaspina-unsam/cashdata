from datetime import date
from unittest.mock import Mock
import pytest

from app.application.use_cases.list_statements_by_credit_card_use_case import (
    ListStatementByCreditCardUseCase,
    ListStatementByCreditCardQuery,
)
from app.domain.entities.monthly_statement import MonthlyStatement
from app.domain.entities.credit_card import CreditCard
from app.application.exceptions.application_exceptions import (
    CreditCardNotFoundError,
    CreditCardOwnerMismatchError,
)


@pytest.fixture
def uow_mock():
    uow = Mock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=False)
    uow.credit_cards = Mock()
    uow.monthly_statements = Mock()
    uow.commit = Mock()
    uow.rollback = Mock()
    return uow


@pytest.fixture
def make_credit_card():
    def _make(id, user_id, name="Test Card"):
        return CreditCard(
            id=id,
            user_id=user_id,
            name=name,
            bank="Test Bank",
            last_four_digits="1234",
            billing_close_day=15,
            payment_due_day=10,
        )
    return _make


@pytest.fixture
def make_statement():
    def _make(id, credit_card_id, start_date, closing_date, due_date):
        return MonthlyStatement(
            id=id,
            credit_card_id=credit_card_id,
            start_date=start_date,
            closing_date=closing_date,
            due_date=due_date,
        )
    return _make


@pytest.fixture
def use_case(uow_mock):
    return ListStatementByCreditCardUseCase(uow_mock)


class TestListStatementByCreditCardUseCaseIntegration:
    def test_raises_credit_card_not_found_when_credit_card_does_not_exist(
        self, uow_mock, use_case
    ):
        uow_mock.credit_cards.find_by_id.return_value = None
        query = ListStatementByCreditCardQuery(user_id=1, credit_card_id=1)

        with pytest.raises(CreditCardNotFoundError, match="Credit card with ID 1 not found"):
            use_case.execute(query)

        uow_mock.credit_cards.find_by_id.assert_called_once_with(1)
        uow_mock.monthly_statements.find_by_credit_card_id.assert_not_called()

    def test_raises_credit_card_owner_mismatch_when_user_does_not_own_credit_card(
        self, uow_mock, make_credit_card, use_case
    ):
        credit_card = make_credit_card(id=1, user_id=2)
        uow_mock.credit_cards.find_by_id.return_value = credit_card
        query = ListStatementByCreditCardQuery(user_id=1, credit_card_id=1)

        with pytest.raises(
            CreditCardOwnerMismatchError,
            match="Credit card 1 does not belong to user 1"
        ):
            use_case.execute(query)

        uow_mock.credit_cards.find_by_id.assert_called_once_with(1)
        uow_mock.monthly_statements.find_by_credit_card_id.assert_not_called()

    def test_returns_sorted_statements_when_credit_card_exists_and_belongs_to_user(
        self, uow_mock, make_credit_card, make_statement, use_case
    ):
        credit_card = make_credit_card(id=1, user_id=1)
        uow_mock.credit_cards.find_by_id.return_value = credit_card

        statement1 = make_statement(
            id=1,
            credit_card_id=1,
            start_date=date(2025, 1, 1),
            closing_date=date(2025, 1, 31),
            due_date=date(2025, 2, 15),
        )
        statement2 = make_statement(
            id=2,
            credit_card_id=1,
            start_date=date(2025, 2, 1),
            closing_date=date(2025, 2, 28),
            due_date=date(2025, 3, 15),
        )
        statement3 = make_statement(
            id=3,
            credit_card_id=1,
            start_date=date(2025, 3, 1),
            closing_date=date(2025, 3, 31),
            due_date=date(2025, 4, 15),
        )
        uow_mock.monthly_statements.find_by_credit_card_id.return_value = [
            statement3, statement1, statement2
        ]  # Unsorted

        query = ListStatementByCreditCardQuery(user_id=1, credit_card_id=1)
        result = use_case.execute(query)

        uow_mock.credit_cards.find_by_id.assert_called_once_with(1)
        uow_mock.monthly_statements.find_by_credit_card_id.assert_called_once_with(1)
        
        # Check that statements are sorted by due_date
        assert len(result) == 3
        assert result[0].due_date == date(2025, 2, 15)
        assert result[1].due_date == date(2025, 3, 15)
        assert result[2].due_date == date(2025, 4, 15)

    def test_returns_empty_list_when_no_statements_exist(
        self, uow_mock, make_credit_card, use_case
    ):
        credit_card = make_credit_card(id=1, user_id=1)
        uow_mock.credit_cards.find_by_id.return_value = credit_card
        uow_mock.monthly_statements.find_by_credit_card_id.return_value = []

        query = ListStatementByCreditCardQuery(user_id=1, credit_card_id=1)
        result = use_case.execute(query)

        assert result == []

    def test_does_not_commit_changes(self, uow_mock, make_credit_card, make_statement, use_case):
        credit_card = make_credit_card(id=1, user_id=1)
        uow_mock.credit_cards.find_by_id.return_value = credit_card
        statement = make_statement(
            id=1,
            credit_card_id=1,
            start_date=date(2025, 1, 1),
            closing_date=date(2025, 1, 31),
            due_date=date(2025, 2, 15),
        )
        uow_mock.monthly_statements.find_by_credit_card_id.return_value = [statement]

        query = ListStatementByCreditCardQuery(user_id=1, credit_card_id=1)
        use_case.execute(query)

        uow_mock.commit.assert_not_called()

    def test_sorts_statements_by_due_date_ascending(self, uow_mock, make_credit_card, make_statement, use_case):
        credit_card = make_credit_card(id=1, user_id=1)
        uow_mock.credit_cards.find_by_id.return_value = credit_card

        statement1 = make_statement(
            id=1,
            credit_card_id=1,
            start_date=date(2025, 1, 1),
            closing_date=date(2025, 1, 31),
            due_date=date(2025, 2, 10),
        )
        statement2 = make_statement(
            id=2,
            credit_card_id=1,
            start_date=date(2025, 2, 1),
            closing_date=date(2025, 2, 28),
            due_date=date(2025, 3, 10),
        )
        statement3 = make_statement(
            id=3,
            credit_card_id=1,
            start_date=date(2025, 3, 1),
            closing_date=date(2025, 3, 31),
            due_date=date(2025, 4, 10),
        )
        uow_mock.monthly_statements.find_by_credit_card_id.return_value = [
            statement2, statement3, statement1
        ]  # Different order

        query = ListStatementByCreditCardQuery(user_id=1, credit_card_id=1)
        result = use_case.execute(query)

        assert len(result) == 3
        assert result[0].due_date == date(2025, 2, 10)
        assert result[1].due_date == date(2025, 3, 10)
        assert result[2].due_date == date(2025, 4, 10)