# backend/tests/unit/domain/test_budget_expense_responsibility.py
import pytest
from decimal import Decimal
from app.domain.entities.budget_expense_responsibility import BudgetExpenseResponsibility
from app.domain.value_objects.money import Money
from app.domain.exceptions.domain_exceptions import InvalidEntity


class TestBudgetExpenseResponsibilityCreation:
    """Tests de creación de BudgetExpenseResponsibility"""

    def test_should_create_responsibility_with_valid_data(self):
        responsible_amount = Money(6250, "ARS")

        responsibility = BudgetExpenseResponsibility(
            id=1,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("50.00"),
            responsible_amount=responsible_amount
        )

        assert responsibility.id == 1
        assert responsibility.budget_expense_id == 1
        assert responsibility.user_id == 1
        assert responsibility.percentage == Decimal("50.00")
        assert responsibility.responsible_amount == responsible_amount

    def test_should_create_responsibility_with_none_id(self):
        responsible_amount = Money(0, "ARS")

        responsibility = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("0.00"),
            responsible_amount=responsible_amount
        )

        assert responsibility.id is None

    def test_should_create_responsibility_with_zero_percentage(self):
        responsible_amount = Money(0, "ARS")

        responsibility = BudgetExpenseResponsibility(
            id=1,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("0.00"),
            responsible_amount=responsible_amount
        )

        assert responsibility.percentage == Decimal("0.00")

    def test_should_create_responsibility_with_hundred_percentage(self):
        responsible_amount = Money(12500, "ARS")

        responsibility = BudgetExpenseResponsibility(
            id=1,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("100.00"),
            responsible_amount=responsible_amount
        )

        assert responsibility.percentage == Decimal("100.00")

    def test_should_raise_exception_when_percentage_is_negative(self):
        responsible_amount = Money(1000, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpenseResponsibility(
                id=1,
                budget_expense_id=1,
                user_id=1,
                percentage=Decimal("-5.00"),  # Invalid
                responsible_amount=responsible_amount
            )

        assert "percentage must be between 0 and 100" in str(err_desc.value).lower()

    def test_should_raise_exception_when_percentage_exceeds_hundred(self):
        responsible_amount = Money(1000, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpenseResponsibility(
                id=1,
                budget_expense_id=1,
                user_id=1,
                percentage=Decimal("150.00"),  # Invalid
                responsible_amount=responsible_amount
            )

        assert "percentage must be between 0 and 100" in str(err_desc.value).lower()

    def test_should_raise_exception_when_responsible_amount_is_negative(self):
        responsible_amount = Money(-100, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpenseResponsibility(
                id=1,
                budget_expense_id=1,
                user_id=1,
                percentage=Decimal("10.00"),
                responsible_amount=responsible_amount  # Invalid
            )

        assert "responsible amount cannot be negative" in str(err_desc.value).lower()

    def test_should_raise_exception_when_budget_expense_id_is_zero(self):
        responsible_amount = Money(1000, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpenseResponsibility(
                id=1,
                budget_expense_id=0,  # Invalid
                user_id=1,
                percentage=Decimal("50.00"),
                responsible_amount=responsible_amount
            )

        assert "budget_expense_id must be positive" in str(err_desc.value).lower()

    def test_should_raise_exception_when_user_id_is_zero(self):
        responsible_amount = Money(1000, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpenseResponsibility(
                id=1,
                budget_expense_id=1,
                user_id=0,  # Invalid
                percentage=Decimal("50.00"),
                responsible_amount=responsible_amount
            )

        assert "user_id must be positive" in str(err_desc.value).lower()


class TestBudgetExpenseResponsibilityMethods:
    """Tests de métodos de BudgetExpenseResponsibility"""

    def test_should_return_string_representation(self):
        responsible_amount = Money(6250, "ARS")

        responsibility = BudgetExpenseResponsibility(
            id=1,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("50.00"),
            responsible_amount=responsible_amount
        )

        expected = "BudgetExpenseResponsibility(user_1, 50.00%, 6250 ARS)"
        assert str(responsibility) == expected