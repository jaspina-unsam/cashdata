# backend/tests/unit/domain/test_budget_balance_calculator.py
import pytest
from datetime import datetime, date
from decimal import Decimal
from app.domain.services.budget_balance_calculator import BudgetBalanceCalculator
from app.domain.entities.budget_with_expenses import BudgetWithExpenses
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.entities.budget_expense import BudgetExpense
from app.domain.entities.budget_expense_responsibility import BudgetExpenseResponsibility
from app.domain.value_objects.money import Money
from app.domain.value_objects.period import Period
from app.domain.value_objects.budget_status import BudgetStatus
from app.domain.value_objects.split_type import SplitType


class TestBudgetBalanceCalculator:
    """Tests para BudgetBalanceCalculator"""

    def test_calculate_balance_user_owes_money(self):
        calculator = BudgetBalanceCalculator()
        budget = self._create_test_budget_with_expenses()

        # User 2 paid 0 but is responsible for 6250 -> owes 6250
        balance = calculator.calculate_balance(budget, 2)
        assert balance == Money(-6250, "ARS")  # Negative = owes

    def test_calculate_balance_user_is_owed_money(self):
        calculator = BudgetBalanceCalculator()
        budget = self._create_test_budget_with_expenses()

        # User 1 paid 12500 but is only responsible for 6250 -> is owed 6250
        balance = calculator.calculate_balance(budget, 1)
        assert balance == Money(6250, "ARS")  # Positive = owed

    def test_calculate_balance_balanced_user(self):
        calculator = BudgetBalanceCalculator()
        budget = self._create_balanced_budget()

        # User paid exactly what they're responsible for
        balance = calculator.calculate_balance(budget, 1)
        assert balance == Money(0, "ARS")

    def test_calculate_debt_summary_simple_case(self):
        calculator = BudgetBalanceCalculator()
        budget = self._create_test_budget_with_expenses()

        debt_summary = calculator.calculate_debt_summary(budget)

        # Should have one debt: user 2 owes 6250 to user 1
        assert len(debt_summary) == 1
        debt = debt_summary[0]
        assert debt["from_user_id"] == 2
        assert debt["to_user_id"] == 1
        assert debt["amount"] == Money(6250, "ARS")

    def test_calculate_debt_summary_no_debts(self):
        calculator = BudgetBalanceCalculator()
        budget = self._create_balanced_budget()

        debt_summary = calculator.calculate_debt_summary(budget)

        assert debt_summary == []

    def _create_test_budget_with_expenses(self) -> BudgetWithExpenses:
        """Create a test budget where user 1 owes user 2"""
        budget = MonthlyBudget(
            id=1,
            name="Test Budget",
            period=Period(2026, 1),
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=datetime(2026, 1, 12, 10, 0, 0),
            updated_at=None
        )

        expenses = [
            BudgetExpense(
                id=1,
                budget_id=1,
                purchase_id=100,
                installment_id=None,
                paid_by_user_id=1,  # User 1 paid
                split_type=SplitType.EQUAL,
                amount=Money(12500, "ARS"),
                currency="ARS",
                description="Supermercado",
                date=date(2026, 1, 15),
                payment_method_name="Visa",
                created_at=date(2026, 1, 15)
            )
        ]

        responsibilities = {
            1: [
                BudgetExpenseResponsibility(
                    id=1, budget_expense_id=1, user_id=1,
                    percentage=Decimal("50"), responsible_amount=Money(6250, "ARS")
                ),
                BudgetExpenseResponsibility(
                    id=2, budget_expense_id=1, user_id=2,
                    percentage=Decimal("50"), responsible_amount=Money(6250, "ARS")
                ),
            ]
        }

        return BudgetWithExpenses(
            budget=budget,
            expenses=expenses,
            responsibilities=responsibilities
        )

    def _create_balanced_budget(self) -> BudgetWithExpenses:
        """Create a test budget where users are balanced"""
        budget = MonthlyBudget(
            id=1,
            name="Balanced Budget",
            period=Period(2026, 1),
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=datetime(2026, 1, 12, 10, 0, 0),
            updated_at=None
        )

        expenses = [
            BudgetExpense(
                id=1,
                budget_id=1,
                purchase_id=100,
                installment_id=None,
                paid_by_user_id=1,
                split_type=SplitType.EQUAL,
                amount=Money(10000, "ARS"),
                currency="ARS",
                description="Balanced expense",
                date=date(2026, 1, 15),
                payment_method_name="Cash",
                created_at=date(2026, 1, 15)
            )
        ]

        responsibilities = {
            1: [
                BudgetExpenseResponsibility(
                    id=1, budget_expense_id=1, user_id=1,
                    percentage=Decimal("100"), responsible_amount=Money(10000, "ARS")
                ),
            ]
        }

        return BudgetWithExpenses(
            budget=budget,
            expenses=expenses,
            responsibilities=responsibilities
        )