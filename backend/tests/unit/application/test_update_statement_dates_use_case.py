from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.application.use_cases.update_statement_dates_use_case import (
    UpdateStatementDatesUseCase,
)
from app.domain.entities.monthly_statement import MonthlyStatement
from app.domain.entities.credit_card import CreditCard
from app.domain.value_objects.money import Money, Currency
from app.domain.entities.installment import Installment
from app.domain.entities.purchase import Purchase


@pytest.fixture
def uow_mock():
    uow = Mock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=False)
    uow.monthly_statements = Mock()
    uow.credit_cards = Mock()
    uow.purchases = Mock()
    uow.installments = Mock()
    return uow


def make_credit_card(id=2, user_id=1):
    return CreditCard(
        id=id,
        payment_method_id=id,
        user_id=user_id,
        name="Card",
        bank="Bank",
        last_four_digits="1111",
        billing_close_day=30,
        payment_due_day=10,
    )


def make_purchase(id=1, payment_method_id=2):
    return Purchase(
        id=id,
        user_id=1,
        payment_method_id=payment_method_id,
        category_id=1,
        purchase_date=date(2025, 8, 15),
        description="Test",
        total_amount=Money(Decimal("100"), Currency.ARS),
        installments_count=1,
    )


def make_installment(id, purchase_id, billing_period, manual_id=None):
    return Installment(
        id=id,
        purchase_id=purchase_id,
        installment_number=1,
        total_installments=1,
        amount=Money(Decimal("100"), Money.currency),
        billing_period=billing_period,
        manually_assigned_statement_id=manual_id,
    )


def test_preserves_included_installments_on_date_change(uow_mock):
    # Setup
    old_statement = MonthlyStatement(
        id=10,
        credit_card_id=2,
        start_date=date(2025, 8, 31),
        closing_date=date(2025, 9, 30),
        due_date=date(2025, 10, 10),
    )

    uow_mock.monthly_statements.find_by_id.return_value = old_statement
    saved_statement = MonthlyStatement(
        id=10,
        credit_card_id=2,
        start_date=date(2025, 9, 1),
        closing_date=date(2025, 10, 2),
        due_date=date(2025, 11, 10),
    )
    uow_mock.monthly_statements.save.return_value = saved_statement

    credit_card = make_credit_card()
    uow_mock.credit_cards.find_by_id.return_value = credit_card

    purchase = make_purchase()
    uow_mock.purchases.find_by_user_id.return_value = [purchase]

    # Installment that belonged to old period (202509)
    inst = make_installment(id=101, purchase_id=purchase.id, billing_period="202509")
    uow_mock.installments.find_by_purchase_id.return_value = [inst]

    # Make sure find_by_id returns the same installment when reassigned
    uow_mock.installments.find_by_id.return_value = inst

    use_case = UpdateStatementDatesUseCase(
        statement_repository=uow_mock.monthly_statements,
        credit_card_repository=uow_mock.credit_cards,
        purchase_repository=uow_mock.purchases,
        installment_repository=uow_mock.installments,
    )

    # Execute: change closing_date so period moves from 202509 to 202510
    input_dto = Mock()
    input_dto.start_date = None
    input_dto.closing_date = date(2025, 10, 2)
    input_dto.due_date = date(2025, 11, 10)

    result = use_case.execute(statement_id=10, user_id=1, input_dto=input_dto)

    # Verify statement saved
    uow_mock.monthly_statements.save.assert_called()

    # Verify at least one save of installment happened with manually_assigned_statement_id equal to statement id
    saves = [call.args[0] for call in uow_mock.installments.save.call_args_list]
    assert any(s.manually_assigned_statement_id == saved_statement.id for s in saves), (
        "Expected at least one installment to be saved with manually_assigned_statement_id set to the updated statement id"
    )