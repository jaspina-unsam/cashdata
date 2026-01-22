# backend/tests/unit/domain/test_budget_with_expenses.py
import pytest
from datetime import datetime, date
from decimal import Decimal
from app.domain.entities.budget_with_expenses import BudgetWithExpenses
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.entities.budget_expense import BudgetExpense
from app.domain.entities.budget_expense_responsibility import BudgetExpenseResponsibility
from app.domain.value_objects.budget_status import BudgetStatus
from app.domain.value_objects.money import Money
from app.domain.value_objects.split_type import SplitType


class TestBudgetWithExpensesCalculations:
    """Tests de cálculos del aggregate BudgetWithExpenses"""

    def test_total_amount_should_return_zero_for_empty_budget(self):
        budget = self._create_test_budget()
        aggregate = BudgetWithExpenses(
            budget=budget,
            expenses=[],
            responsibilities={}
        )

        total = aggregate.total_amount()
        assert total == Money(0, "ARS")

    def test_total_amount_should_sum_all_expenses(self):
        budget = self._create_test_budget()
        expenses = [
            self._create_test_expense(1, 12500, "ARS"),
            self._create_test_expense(2, 8000, "ARS"),
            self._create_test_expense(3, 3800, "ARS")
        ]
        aggregate = BudgetWithExpenses(
            budget=budget,
            expenses=expenses,
            responsibilities={}
        )

        total = aggregate.total_amount()
        assert total == Money(24300, "ARS")

    def test_amount_paid_by_should_return_zero_when_user_paid_nothing(self):
        budget = self._create_test_budget()
        expenses = [
            self._create_test_expense(1, 12500, "ARS", paid_by_user_id=2),
        ]
        aggregate = BudgetWithExpenses(
            budget=budget,
            expenses=expenses,
            responsibilities={}
        )

        paid = aggregate.amount_paid_by(1)  # User 1 paid nothing
        assert paid == Money(0, "ARS")

    def test_amount_paid_by_should_sum_expenses_paid_by_user(self):
        budget = self._create_test_budget()
        expenses = [
            self._create_test_expense(1, 12500, "ARS", paid_by_user_id=1),
            self._create_test_expense(2, 8000, "ARS", paid_by_user_id=1),
            self._create_test_expense(3, 3800, "ARS", paid_by_user_id=2),
        ]
        aggregate = BudgetWithExpenses(
            budget=budget,
            expenses=expenses,
            responsibilities={}
        )

        paid_by_1 = aggregate.amount_paid_by(1)
        paid_by_2 = aggregate.amount_paid_by(2)

        assert paid_by_1 == Money(20500, "ARS")
        assert paid_by_2 == Money(3800, "ARS")

    def test_amount_responsible_for_should_return_zero_when_no_responsibilities(self):
        budget = self._create_test_budget()
        expenses = [self._create_test_expense(1, 12500, "ARS")]
        responsibilities = {}  # No responsibilities defined
        aggregate = BudgetWithExpenses(
            budget=budget,
            expenses=expenses,
            responsibilities=responsibilities
        )

        responsible = aggregate.amount_responsible_for(1)
        assert responsible == Money(0, "ARS")

    def test_amount_responsible_for_should_sum_user_responsibilities(self):
        budget = self._create_test_budget()
        expenses = [self._create_test_expense(1, 12500, "ARS")]
        responsibilities = {
            1: [
                BudgetExpenseResponsibility(
                    id=1, budget_expense_id=1, user_id=1,
                    percentage=Decimal("60"), responsible_amount=Money(7500, "ARS")
                ),
                BudgetExpenseResponsibility(
                    id=2, budget_expense_id=1, user_id=2,
                    percentage=Decimal("40"), responsible_amount=Money(5000, "ARS")
                ),
            ]
        }
        aggregate = BudgetWithExpenses(
            budget=budget,
            expenses=expenses,
            responsibilities=responsibilities
        )

        responsible_1 = aggregate.amount_responsible_for(1)
        responsible_2 = aggregate.amount_responsible_for(2)

        assert responsible_1 == Money(7500, "ARS")
        assert responsible_2 == Money(5000, "ARS")

    def test_net_balance_should_calculate_paid_minus_responsible(self):
        budget = self._create_test_budget()
        expenses = [self._create_test_expense(1, 12500, "ARS", paid_by_user_id=1)]
        responsibilities = {
            1: [
                BudgetExpenseResponsibility(
                    id=1, budget_expense_id=1, user_id=1,
                    percentage=Decimal("60"), responsible_amount=Money(7500, "ARS")
                ),
                BudgetExpenseResponsibility(
                    id=2, budget_expense_id=1, user_id=2,
                    percentage=Decimal("40"), responsible_amount=Money(5000, "ARS")
                ),
            ]
        }
        aggregate = BudgetWithExpenses(
            budget=budget,
            expenses=expenses,
            responsibilities=responsibilities
        )

        balance_1 = aggregate.net_balance(1)  # Paid 12500, responsible 7500 -> +5000
        balance_2 = aggregate.net_balance(2)  # Paid 0, responsible 5000 -> -5000

        assert balance_1 == Money(5000, "ARS")
        assert balance_2 == Money(-5000, "ARS")

    def test_get_participants_should_include_creator_and_responsibility_users(self):
        budget = self._create_test_budget(created_by_user_id=1)
        expenses = [self._create_test_expense(1, 12500, "ARS")]
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
        aggregate = BudgetWithExpenses(
            budget=budget,
            expenses=expenses,
            responsibilities=responsibilities
        )

        participants = aggregate.get_participants()
        assert participants == [1, 2]

    def test_calculate_debt_summary_should_return_empty_for_balanced_budget(self):
        budget = self._create_test_budget()
        # User 1 pays what they're responsible for (5000), User 2 pays what they're responsible for (5000)
        expenses = [
            self._create_test_expense(1, 5000, "ARS", paid_by_user_id=1),
            self._create_test_expense(2, 5000, "ARS", paid_by_user_id=2)
        ]
        responsibilities = {
            1: [
                BudgetExpenseResponsibility(
                    id=1, budget_expense_id=1, user_id=1,
                    percentage=Decimal("100"), responsible_amount=Money(5000, "ARS")
                ),
            ],
            2: [
                BudgetExpenseResponsibility(
                    id=2, budget_expense_id=2, user_id=2,
                    percentage=Decimal("100"), responsible_amount=Money(5000, "ARS")
                ),
            ]
        }
        aggregate = BudgetWithExpenses(
            budget=budget,
            expenses=expenses,
            responsibilities=responsibilities
        )

        debts = aggregate.calculate_debt_summary()
        assert debts == []

    def test_calculate_debt_summary_should_calculate_simple_debt(self):
        budget = self._create_test_budget()
        expenses = [self._create_test_expense(1, 10000, "ARS", paid_by_user_id=1)]
        responsibilities = {
            1: [
                BudgetExpenseResponsibility(
                    id=1, budget_expense_id=1, user_id=1,
                    percentage=Decimal("0"), responsible_amount=Money(0, "ARS")
                ),
                BudgetExpenseResponsibility(
                    id=2, budget_expense_id=1, user_id=2,
                    percentage=Decimal("100"), responsible_amount=Money(10000, "ARS")
                ),
            ]
        }
        aggregate = BudgetWithExpenses(
            budget=budget,
            expenses=expenses,
            responsibilities=responsibilities
        )

        debts = aggregate.calculate_debt_summary()

        # User 2 owes 10000 to user 1 (user 1 paid, user 2 is responsible)
        assert len(debts) == 1
        assert debts[0]["from_user_id"] == 2
        assert debts[0]["to_user_id"] == 1
        assert debts[0]["amount"] == Money(10000, "ARS")

    def _create_test_budget(self, created_by_user_id: int = 1) -> MonthlyBudget:
        """Helper to create a test budget"""
        return MonthlyBudget(
            id=1,
            name="Test Budget",
            description="Test budget for calculations",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=created_by_user_id,
            created_at=datetime(2026, 1, 12, 10, 0, 0),
            updated_at=None
        )

    def _create_test_expense(
        self,
        expense_id: int,
        amount: int,
        currency: str,
        paid_by_user_id: int = 1
    ) -> BudgetExpense:
        """Helper to create a test expense"""
        return BudgetExpense(
            id=expense_id,
            budget_id=1,
            purchase_id=expense_id * 100,
            installment_id=None,
            paid_by_user_id=paid_by_user_id,
            split_type=SplitType.EQUAL,
            amount=Money(amount, currency),
            currency=currency,
            description=f"Test expense {expense_id}",
            date=date(2026, 1, 15),
            payment_method_name="Test Card",
            created_at=date(2026, 1, 15)
        )