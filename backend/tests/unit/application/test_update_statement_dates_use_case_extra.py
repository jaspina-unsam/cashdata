from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from app.application.use_cases.update_statement_dates_use_case import (
    UpdateStatementDatesUseCase,
)
from app.domain.entities.monthly_statement import MonthlyStatement
from app.domain.entities.credit_card import CreditCard
from app.domain.value_objects.money import Money, Currency
from app.domain.entities.installment import Installment
from app.domain.entities.purchase import Purchase


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


def make_purchase(id=1, payment_method_id=2, purchase_date=date(2025, 11, 15)):
    return Purchase(
        id=id,
        user_id=1,
        payment_method_id=payment_method_id,
        category_id=1,
        purchase_date=purchase_date,
        description="Test",
        total_amount=Money(Decimal("100"), Currency.ARS),
        installments_count=1,
    )


def make_installment(id, purchase_id, billing_period, manual_id=None):
    return Installment(
        id=id,
        purchase_id=purchase_id,
        installment_number=1,
        total_installments=6,
        amount=Money(Decimal("100"), Currency.ARS),
        billing_period=billing_period,
        manually_assigned_statement_id=manual_id,
    )


def test_does_not_steal_installments_from_next_statement():
    # Setup two statements: current closes 2025-11-30, next closes 2025-12-30
    old_statement = MonthlyStatement(
        id=10,
        credit_card_id=2,
        start_date=date(2025, 10, 31),
        closing_date=date(2025, 11, 30),
        due_date=date(2025, 12, 10),
    )

    next_statement = MonthlyStatement(
        id=11,
        credit_card_id=2,
        start_date=date(2025, 12, 1),
        closing_date=date(2025, 12, 30),
        due_date=date(2026, 1, 10),
    )

    uow_mock = Mock()
    uow_mock.monthly_statements.find_by_id.return_value = old_statement
    uow_mock.monthly_statements.save.return_value = MonthlyStatement(
        id=10,
        credit_card_id=2,
        start_date=date(2025, 11, 1),
        closing_date=date(2025, 12, 2),
        due_date=date(2026, 1, 10),
    )

    uow_mock.monthly_statements.find_by_credit_card_id.return_value = [old_statement, next_statement]

    credit_card = make_credit_card()
    uow_mock.credit_cards.find_by_id.return_value = credit_card

    # Purchases: one in old period, one in next period
    purchase_old = make_purchase(id=1, purchase_date=date(2025, 11, 15))
    purchase_next = make_purchase(id=2, purchase_date=date(2025, 12, 15))
    uow_mock.purchases.find_by_user_id.return_value = [purchase_old, purchase_next]

    # Installments: old one in 202511, next one in 202512 and manually assigned to next_statement
    inst_old = make_installment(id=101, purchase_id=1, billing_period="202511")
    inst_next = make_installment(id=102, purchase_id=2, billing_period="202512", manual_id=11)

    def find_by_purchase_id(pid):
        return [inst_old] if pid == 1 else [inst_next]

    uow_mock.installments.find_by_purchase_id.side_effect = find_by_purchase_id
    uow_mock.installments.find_by_id.side_effect = lambda i: inst_old if i == 101 else inst_next

    use_case = UpdateStatementDatesUseCase(
        statement_repository=uow_mock.monthly_statements,
        credit_card_repository=uow_mock.credit_cards,
        purchase_repository=uow_mock.purchases,
        installment_repository=uow_mock.installments,
    )

    # Execute change: extend closing date so old statement now covers both months
    input_dto = Mock()
    input_dto.start_date = None
    input_dto.closing_date = date(2025, 12, 2)
    input_dto.due_date = date(2026, 1, 10)

    result = use_case.execute(statement_id=10, user_id=1, input_dto=input_dto)

    # Verify that the installment that originally belonged to next statement keeps its manual assignment
    assert inst_next.manually_assigned_statement_id == 11

    # Also make sure that the old installment was preserved and assigned to the updated statement
    saves = [call.args[0] for call in uow_mock.installments.save.call_args_list]
    assert any(s.manually_assigned_statement_id == 10 for s in saves)
