import pytest
from datetime import date
from decimal import Decimal

from app.domain.entities.budget_expense import BudgetExpense
from app.domain.value_objects.money import Money
from app.domain.value_objects.split_type import SplitType
from app.infrastructure.persistence.repositories.sqlalchemy_budget_expense_repository import SQLAlchemyBudgetExpenseRepository


class TestBudgetExpenseRepository:
    def test_save_and_find_by_id(self, db_session):
        """Test saving and retrieving a budget expense"""
        repo = SQLAlchemyBudgetExpenseRepository(db_session)

        expense = BudgetExpense(
            id=None,
            budget_id=1,
            purchase_id=1,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=Money(Decimal("1000.50"), "ARS"),
            currency="ARS",
            description="Test expense from purchase",
            date=date(2026, 1, 15),
            payment_method_name="Credit Card",
            created_at=date(2026, 1, 15),
        )

        # Save expense
        saved_expense = repo.save(expense)
        assert saved_expense.id is not None
        assert saved_expense.budget_id == 1
        assert saved_expense.purchase_id == 1
        assert saved_expense.installment_id is None
        assert saved_expense.paid_by_user_id == 1
        assert saved_expense.split_type == SplitType.EQUAL
        assert saved_expense.amount == Money(Decimal("1000.50"), "ARS")
        assert saved_expense.description == "Test expense from purchase"
        assert saved_expense.date == date(2026, 1, 15)
        assert saved_expense.payment_method_name == "Credit Card"

        # Find by ID
        found_expense = repo.find_by_id(saved_expense.id)
        assert found_expense is not None
        assert found_expense.id == saved_expense.id
        assert found_expense.budget_id == saved_expense.budget_id
        assert found_expense.purchase_id == saved_expense.purchase_id
        assert found_expense.split_type == saved_expense.split_type
        assert found_expense.amount == saved_expense.amount

    def test_find_by_budget_id(self, db_session):
        """Test finding expenses by budget ID"""
        repo = SQLAlchemyBudgetExpenseRepository(db_session)

        # Create multiple expenses for the same budget
        expense1 = BudgetExpense(
            id=None,
            budget_id=1,
            purchase_id=1,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=Money(Decimal("500"), "ARS"),
            currency="ARS",
            description="Expense 1",
            date=date(2026, 1, 10),
            payment_method_name=None,
            created_at=date(2026, 1, 10),
        )

        expense2 = BudgetExpense(
            id=None,
            budget_id=1,
            purchase_id=None,
            installment_id=1,
            paid_by_user_id=2,
            split_type=SplitType.PROPORTIONAL,
            amount=Money(Decimal("750"), "ARS"),
            currency="ARS",
            description="Expense 2",
            date=date(2026, 1, 12),
            payment_method_name="Cash",
            created_at=date(2026, 1, 12),
        )

        expense3 = BudgetExpense(
            id=None,
            budget_id=2,  # Different budget
            purchase_id=2,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.FULL_SINGLE,
            amount=Money(Decimal("200"), "ARS"),
            currency="ARS",
            description="Expense 3",
            date=date(2026, 1, 14),
            payment_method_name=None,
            created_at=date(2026, 1, 14),
        )

        expense1 = repo.save(expense1)
        expense2 = repo.save(expense2)
        expense3 = repo.save(expense3)

        # Find expenses for budget 1
        budget_1_expenses = repo.find_by_budget_id(1)
        assert len(budget_1_expenses) == 2

        # Check that both expenses belong to budget 1
        expense_ids = [e.id for e in budget_1_expenses]
        assert expense1.id in expense_ids
        assert expense2.id in expense_ids

        # Find expenses for budget 2
        budget_2_expenses = repo.find_by_budget_id(2)
        assert len(budget_2_expenses) == 1
        assert budget_2_expenses[0].id == expense3.id

        # Find expenses for non-existent budget
        empty_expenses = repo.find_by_budget_id(999)
        assert len(empty_expenses) == 0

    def test_find_by_purchase_id(self, db_session):
        """Test finding expenses by purchase ID"""
        repo = SQLAlchemyBudgetExpenseRepository(db_session)

        expense1 = BudgetExpense(
            id=None,
            budget_id=1,
            purchase_id=1,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=Money(Decimal("300"), "ARS"),
            currency="ARS",
            description="Purchase expense 1",
            date=date(2026, 1, 10),
            payment_method_name=None,
            created_at=date(2026, 1, 10),
        )

        expense2 = BudgetExpense(
            id=None,
            budget_id=1,
            purchase_id=1,  # Same purchase
            installment_id=None,
            paid_by_user_id=2,
            split_type=SplitType.EQUAL,
            amount=Money(Decimal("200"), "ARS"),
            currency="ARS",
            description="Purchase expense 2",
            date=date(2026, 1, 10),
            payment_method_name=None,
            created_at=date(2026, 1, 10),
        )

        expense3 = BudgetExpense(
            id=None,
            budget_id=2,
            purchase_id=2,  # Different purchase
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.FULL_SINGLE,
            amount=Money(Decimal("150"), "ARS"),
            currency="ARS",
            description="Different purchase",
            date=date(2026, 1, 12),
            payment_method_name=None,
            created_at=date(2026, 1, 12),
        )

        expense1 = repo.save(expense1)
        expense2 = repo.save(expense2)
        expense3 = repo.save(expense3)

        # Find expenses for purchase 1
        purchase_1_expenses = repo.find_by_purchase_id(1)
        assert len(purchase_1_expenses) == 2

        # Find expenses for purchase 2
        purchase_2_expenses = repo.find_by_purchase_id(2)
        assert len(purchase_2_expenses) == 1
        assert purchase_2_expenses[0].id == expense3.id

        # Find expenses for non-existent purchase
        empty_expenses = repo.find_by_purchase_id(999)
        assert len(empty_expenses) == 0

    def test_find_by_installment_id(self, db_session):
        """Test finding expenses by installment ID"""
        repo = SQLAlchemyBudgetExpenseRepository(db_session)

        expense = BudgetExpense(
            id=None,
            budget_id=1,
            purchase_id=None,
            installment_id=1,
            paid_by_user_id=1,
            split_type=SplitType.PROPORTIONAL,
            amount=Money(Decimal("450"), "ARS"),
            currency="ARS",
            description="Installment expense",
            date=date(2026, 1, 15),
            payment_method_name="Bank Transfer",
            created_at=date(2026, 1, 15),
        )

        saved_expense = repo.save(expense)

        # Find expenses for installment 1
        installment_expenses = repo.find_by_installment_id(1)
        assert len(installment_expenses) == 1
        assert installment_expenses[0].id == saved_expense.id

        # Find expenses for non-existent installment
        empty_expenses = repo.find_by_installment_id(999)
        assert len(empty_expenses) == 0

    def test_find_by_paid_by_user_id(self, db_session):
        """Test finding expenses paid by a specific user"""
        repo = SQLAlchemyBudgetExpenseRepository(db_session)

        expense1 = BudgetExpense(
            id=None,
            budget_id=1,
            purchase_id=1,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=Money(Decimal("250"), "ARS"),
            currency="ARS",
            description="User 1 expense 1",
            date=date(2026, 1, 10),
            payment_method_name=None,
            created_at=date(2026, 1, 10),
        )

        expense2 = BudgetExpense(
            id=None,
            budget_id=2,
            purchase_id=None,
            installment_id=1,
            paid_by_user_id=1,  # Same user
            split_type=SplitType.FULL_SINGLE,
            amount=Money(Decimal("180"), "ARS"),
            currency="ARS",
            description="User 1 expense 2",
            date=date(2026, 1, 12),
            payment_method_name=None,
            created_at=date(2026, 1, 12),
        )

        expense3 = BudgetExpense(
            id=None,
            budget_id=1,
            purchase_id=2,
            installment_id=None,
            paid_by_user_id=2,  # Different user
            split_type=SplitType.CUSTOM,
            amount=Money(Decimal("320"), "ARS"),
            currency="ARS",
            description="User 2 expense",
            date=date(2026, 1, 14),
            payment_method_name=None,
            created_at=date(2026, 1, 14),
        )

        expense1 = repo.save(expense1)
        expense2 = repo.save(expense2)
        expense3 = repo.save(expense3)

        # Find expenses paid by user 1
        user_1_expenses = repo.find_by_paid_by_user_id(1)
        assert len(user_1_expenses) == 2

        # Find expenses paid by user 2
        user_2_expenses = repo.find_by_paid_by_user_id(2)
        assert len(user_2_expenses) == 1
        assert user_2_expenses[0].id == expense3.id

        # Find expenses for non-existent user
        empty_expenses = repo.find_by_paid_by_user_id(999)
        assert len(empty_expenses) == 0

    def test_update_expense(self, db_session):
        """Test updating an existing expense"""
        repo = SQLAlchemyBudgetExpenseRepository(db_session)

        # Create initial expense
        expense = BudgetExpense(
            id=None,
            budget_id=1,
            purchase_id=1,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=Money(Decimal("100"), "ARS"),
            currency="ARS",
            description="Original description",
            date=date(2026, 1, 10),
            payment_method_name="Cash",
            created_at=date(2026, 1, 10),
        )

        saved_expense = repo.save(expense)

        # Update the expense
        updated_expense = BudgetExpense(
            id=saved_expense.id,
            budget_id=saved_expense.budget_id,
            purchase_id=saved_expense.purchase_id,
            installment_id=saved_expense.installment_id,
            paid_by_user_id=saved_expense.paid_by_user_id,
            split_type=SplitType.PROPORTIONAL,  # Changed
            amount=Money(Decimal("150"), "ARS"),  # Changed
            currency="ARS",
            description="Updated description",  # Changed
            date=date(2026, 1, 15),  # Changed
            payment_method_name="Credit Card",  # Changed
            created_at=saved_expense.created_at,
        )

        result = repo.save(updated_expense)

        # Verify updates
        assert result.id == saved_expense.id
        assert result.split_type == SplitType.PROPORTIONAL
        assert result.amount == Money(Decimal("150"), "ARS")
        assert result.description == "Updated description"
        assert result.date == date(2026, 1, 15)
        assert result.payment_method_name == "Credit Card"

    def test_delete_expense(self, db_session):
        """Test deleting an expense"""
        repo = SQLAlchemyBudgetExpenseRepository(db_session)

        expense = BudgetExpense(
            id=None,
            budget_id=1,
            purchase_id=1,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=Money(Decimal("200"), "ARS"),
            currency="ARS",
            description="Expense to delete",
            date=date(2026, 1, 10),
            payment_method_name=None,
            created_at=date(2026, 1, 10),
        )

        saved_expense = repo.save(expense)

        # Verify it exists
        found = repo.find_by_id(saved_expense.id)
        assert found is not None

        # Delete it
        repo.delete(saved_expense.id)

        # Verify it's gone
        not_found = repo.find_by_id(saved_expense.id)
        assert not_found is None