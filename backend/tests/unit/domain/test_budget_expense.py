# backend/tests/unit/domain/test_budget_expense.py
import pytest
from datetime import date
from app.domain.entities.budget_expense import BudgetExpense
from app.domain.value_objects.money import Money
from app.domain.value_objects.split_type import SplitType
from app.domain.exceptions.domain_exceptions import InvalidEntity


class TestBudgetExpenseCreation:
    """Tests de creación de BudgetExpense"""

    def test_should_create_expense_from_purchase(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(12500, "ARS")

        expense = BudgetExpense(
            id=1,
            budget_id=1,
            purchase_id=100,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=amount,
            currency="ARS",
            description="Supermercado",
            date=expense_date,
            payment_method_name="Visa",
            created_at=created_at
        )

        assert expense.id == 1
        assert expense.budget_id == 1
        assert expense.purchase_id == 100
        assert expense.installment_id is None
        assert expense.paid_by_user_id == 1
        assert expense.split_type == SplitType.EQUAL
        assert expense.amount == amount
        assert expense.currency == "ARS"
        assert expense.description == "Supermercado"
        assert expense.date == expense_date
        assert expense.payment_method_name == "Visa"
        assert expense.created_at == created_at

    def test_should_create_expense_from_installment(self):
        expense_date = date(2026, 1, 18)
        created_at = date(2026, 1, 18)
        amount = Money(3800, "ARS")

        expense = BudgetExpense(
            id=2,
            budget_id=1,
            purchase_id=None,
            installment_id=200,
            paid_by_user_id=2,
            split_type=SplitType.PROPORTIONAL,
            amount=amount,
            currency="ARS",
            description="Netflix cuota 1/12",
            date=expense_date,
            payment_method_name="Efectivo",
            created_at=created_at
        )

        assert expense.purchase_id is None
        assert expense.installment_id == 200

    def test_should_create_expense_with_none_id(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(1000, "ARS")

        expense = BudgetExpense(
            id=None,
            budget_id=1,
            purchase_id=100,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.CUSTOM,
            amount=amount,
            currency="ARS",
            description=None,
            date=expense_date,
            payment_method_name=None,
            created_at=created_at
        )

        assert expense.id is None
        assert expense.description is None
        assert expense.payment_method_name is None

    def test_should_raise_exception_when_both_purchase_and_installment_are_set(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(1000, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpense(
                id=1,
                budget_id=1,
                purchase_id=100,
                installment_id=200,  # Both set - invalid
                paid_by_user_id=1,
                split_type=SplitType.EQUAL,
                amount=amount,
                currency="ARS",
                description="Test",
                date=expense_date,
                payment_method_name="Test",
                created_at=created_at
            )

        assert "exactly one of purchase_id or installment_id must be set" in str(err_desc.value).lower()

    def test_should_raise_exception_when_neither_purchase_nor_installment_are_set(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(1000, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpense(
                id=1,
                budget_id=1,
                purchase_id=None,
                installment_id=None,  # Neither set - invalid
                paid_by_user_id=1,
                split_type=SplitType.EQUAL,
                amount=amount,
                currency="ARS",
                description="Test",
                date=expense_date,
                payment_method_name="Test",
                created_at=created_at
            )

        assert "exactly one of purchase_id or installment_id must be set" in str(err_desc.value).lower()

    def test_should_raise_exception_when_amount_is_zero(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(0, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpense(
                id=1,
                budget_id=1,
                purchase_id=100,
                installment_id=None,
                paid_by_user_id=1,
                split_type=SplitType.EQUAL,
                amount=amount,
                currency="ARS",
                description="Test",
                date=expense_date,
                payment_method_name="Test",
                created_at=created_at
            )

        assert "amount must be positive" in str(err_desc.value).lower()

    def test_should_raise_exception_when_amount_is_negative(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(-100, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpense(
                id=1,
                budget_id=1,
                purchase_id=100,
                installment_id=None,
                paid_by_user_id=1,
                split_type=SplitType.EQUAL,
                amount=amount,
                currency="ARS",
                description="Test",
                date=expense_date,
                payment_method_name="Test",
                created_at=created_at
            )

        assert "amount must be positive" in str(err_desc.value).lower()

    def test_should_raise_exception_when_description_is_empty_string(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(1000, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpense(
                id=1,
                budget_id=1,
                purchase_id=100,
                installment_id=None,
                paid_by_user_id=1,
                split_type=SplitType.EQUAL,
                amount=amount,
                currency="ARS",
                description="",  # Empty string - invalid
                date=expense_date,
                payment_method_name="Test",
                created_at=created_at
            )

        assert "description cannot be empty string" in str(err_desc.value).lower()

    def test_should_raise_exception_when_budget_id_is_zero(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(1000, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpense(
                id=1,
                budget_id=0,  # Invalid
                purchase_id=100,
                installment_id=None,
                paid_by_user_id=1,
                split_type=SplitType.EQUAL,
                amount=amount,
                currency="ARS",
                description="Test",
                date=expense_date,
                payment_method_name="Test",
                created_at=created_at
            )

        assert "budget_id must be positive" in str(err_desc.value).lower()

    def test_should_raise_exception_when_paid_by_user_id_is_zero(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(1000, "ARS")

        with pytest.raises(InvalidEntity) as err_desc:
            BudgetExpense(
                id=1,
                budget_id=1,
                purchase_id=100,
                installment_id=None,
                paid_by_user_id=0,  # Invalid
                split_type=SplitType.EQUAL,
                amount=amount,
                currency="ARS",
                description="Test",
                date=expense_date,
                payment_method_name="Test",
                created_at=created_at
            )

        assert "paid_by_user_id must be positive" in str(err_desc.value).lower()


class TestBudgetExpenseMethods:
    """Tests de métodos de BudgetExpense"""

    def test_should_return_string_representation_for_purchase(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(12500, "ARS")

        expense = BudgetExpense(
            id=1,
            budget_id=1,
            purchase_id=100,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=amount,
            currency="ARS",
            description="Supermercado",
            date=expense_date,
            payment_method_name="Visa",
            created_at=created_at
        )

        expected = "Supermercado - 12500 ARS - paid_by_user_1"
        assert str(expense) == expected

    def test_should_return_string_representation_for_installment(self):
        expense_date = date(2026, 1, 18)
        created_at = date(2026, 1, 18)
        amount = Money(3800, "ARS")

        expense = BudgetExpense(
            id=2,
            budget_id=1,
            purchase_id=None,
            installment_id=200,
            paid_by_user_id=2,
            split_type=SplitType.PROPORTIONAL,
            amount=amount,
            currency="ARS",
            description="Netflix",
            date=expense_date,
            payment_method_name="Efectivo",
            created_at=created_at
        )

        expected = "Netflix - 3800 ARS - paid_by_user_2"
        assert str(expense) == expected

    def test_is_from_purchase_should_return_true_for_purchase_expense(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(1000, "ARS")

        expense = BudgetExpense(
            id=1,
            budget_id=1,
            purchase_id=100,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=amount,
            currency="ARS",
            description="Test",
            date=expense_date,
            payment_method_name="Test",
            created_at=created_at
        )

        assert expense.is_from_purchase() is True
        assert expense.is_from_installment() is False

    def test_is_from_installment_should_return_true_for_installment_expense(self):
        expense_date = date(2026, 1, 18)
        created_at = date(2026, 1, 18)
        amount = Money(1000, "ARS")

        expense = BudgetExpense(
            id=2,
            budget_id=1,
            purchase_id=None,
            installment_id=200,
            paid_by_user_id=2,
            split_type=SplitType.EQUAL,
            amount=amount,
            currency="ARS",
            description="Test",
            date=expense_date,
            payment_method_name="Test",
            created_at=created_at
        )

        assert expense.is_from_purchase() is False
        assert expense.is_from_installment() is True

    def test_get_reference_id_should_return_purchase_id(self):
        expense_date = date(2026, 1, 15)
        created_at = date(2026, 1, 15)
        amount = Money(1000, "ARS")

        expense = BudgetExpense(
            id=1,
            budget_id=1,
            purchase_id=100,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=amount,
            currency="ARS",
            description="Test",
            date=expense_date,
            payment_method_name="Test",
            created_at=created_at
        )

        assert expense.get_reference_id() == 100

    def test_get_reference_id_should_return_installment_id(self):
        expense_date = date(2026, 1, 18)
        created_at = date(2026, 1, 18)
        amount = Money(1000, "ARS")

        expense = BudgetExpense(
            id=2,
            budget_id=1,
            purchase_id=None,
            installment_id=200,
            paid_by_user_id=2,
            split_type=SplitType.EQUAL,
            amount=amount,
            currency="ARS",
            description="Test",
            date=expense_date,
            payment_method_name="Test",
            created_at=created_at
        )

        assert expense.get_reference_id() == 200