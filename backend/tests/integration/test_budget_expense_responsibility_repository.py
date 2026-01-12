import pytest
from datetime import date
from decimal import Decimal

from app.domain.entities.budget_expense_responsibility import BudgetExpenseResponsibility
from app.domain.value_objects.money import Money
from app.infrastructure.persistence.repositories.sqlalchemy_budget_expense_responsibility_repository import SQLAlchemyBudgetExpenseResponsibilityRepository


class TestBudgetExpenseResponsibilityRepository:
    def test_save_and_find_by_id(self, db_session):
        """Test saving and retrieving a budget expense responsibility"""
        repo = SQLAlchemyBudgetExpenseResponsibilityRepository(db_session)

        responsibility = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("50.00"),
            responsible_amount=Money(Decimal("500.00"), "ARS"),
        )

        # Save responsibility
        saved_responsibility = repo.save(responsibility)
        assert saved_responsibility.id is not None
        assert saved_responsibility.budget_expense_id == 1
        assert saved_responsibility.user_id == 1
        assert saved_responsibility.percentage == Decimal("50.00")
        assert saved_responsibility.responsible_amount == Money(Decimal("500.00"), "ARS")

        # Find by ID
        found_responsibility = repo.find_by_id(saved_responsibility.id)
        assert found_responsibility is not None
        assert found_responsibility.id == saved_responsibility.id
        assert found_responsibility.budget_expense_id == saved_responsibility.budget_expense_id
        assert found_responsibility.user_id == saved_responsibility.user_id
        assert found_responsibility.percentage == saved_responsibility.percentage
        assert found_responsibility.responsible_amount == saved_responsibility.responsible_amount

    def test_find_by_budget_expense_id(self, db_session):
        """Test finding responsibilities by budget expense ID"""
        repo = SQLAlchemyBudgetExpenseResponsibilityRepository(db_session)

        # Create multiple responsibilities for the same budget expense
        responsibility1 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("40.00"),
            responsible_amount=Money(Decimal("400.00"), "ARS"),
        )

        responsibility2 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=1,
            user_id=2,
            percentage=Decimal("60.00"),
            responsible_amount=Money(Decimal("600.00"), "ARS"),
        )

        responsibility3 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=2,  # Different budget expense
            user_id=1,
            percentage=Decimal("100.00"),
            responsible_amount=Money(Decimal("200.00"), "ARS"),
        )

        repo.save(responsibility1)
        repo.save(responsibility2)
        repo.save(responsibility3)

        # Find responsibilities for budget expense 1
        expense_1_responsibilities = repo.find_by_budget_expense_id(1)
        assert len(expense_1_responsibilities) == 2

        # Check that both responsibilities belong to budget expense 1
        user_ids = [r.user_id for r in expense_1_responsibilities]
        assert 1 in user_ids
        assert 2 in user_ids

        # Find responsibilities for budget expense 2
        expense_2_responsibilities = repo.find_by_budget_expense_id(2)
        assert len(expense_2_responsibilities) == 1
        assert expense_2_responsibilities[0].user_id == 1

        # Find responsibilities for non-existent budget expense
        empty_responsibilities = repo.find_by_budget_expense_id(999)
        assert len(empty_responsibilities) == 0

    def test_find_by_user_id(self, db_session):
        """Test finding responsibilities by user ID"""
        repo = SQLAlchemyBudgetExpenseResponsibilityRepository(db_session)

        responsibility1 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("50.00"),
            responsible_amount=Money(Decimal("250.00"), "ARS"),
        )

        responsibility2 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=2,
            user_id=1,  # Same user
            percentage=Decimal("30.00"),
            responsible_amount=Money(Decimal("150.00"), "ARS"),
        )

        responsibility3 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=1,
            user_id=2,  # Different user
            percentage=Decimal("50.00"),
            responsible_amount=Money(Decimal("250.00"), "ARS"),
        )

        repo.save(responsibility1)
        repo.save(responsibility2)
        repo.save(responsibility3)

        # Find responsibilities for user 1
        user_1_responsibilities = repo.find_by_user_id(1)
        assert len(user_1_responsibilities) == 2

        # Find responsibilities for user 2
        user_2_responsibilities = repo.find_by_user_id(2)
        assert len(user_2_responsibilities) == 1

        # Find responsibilities for non-existent user
        empty_responsibilities = repo.find_by_user_id(999)
        assert len(empty_responsibilities) == 0

    def test_find_by_budget_id_returns_dict(self, db_session):
        """Test finding responsibilities by budget ID returns dict grouped by budget_expense_id"""
        repo = SQLAlchemyBudgetExpenseResponsibilityRepository(db_session)

        # Create budget expenses first (we need them for the join)
        from app.domain.entities.budget_expense import BudgetExpense
        from app.domain.value_objects.split_type import SplitType
        from app.infrastructure.persistence.repositories.sqlalchemy_budget_expense_repository import SQLAlchemyBudgetExpenseRepository

        budget_repo = SQLAlchemyBudgetExpenseRepository(db_session)

        expense1 = BudgetExpense(
            id=None,
            budget_id=1,  # Same budget
            purchase_id=1,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=Money(Decimal("1000.00"), "ARS"),
            currency="ARS",
            description="Expense 1",
            date=date(2026, 1, 15),
            payment_method_name=None,
            created_at=date(2026, 1, 15),
        )

        expense2 = BudgetExpense(
            id=None,
            budget_id=1,  # Same budget
            purchase_id=None,
            installment_id=1,
            paid_by_user_id=2,
            split_type=SplitType.EQUAL,
            amount=Money(Decimal("500.00"), "ARS"),
            currency="ARS",
            description="Expense 2",
            date=date(2026, 1, 16),
            payment_method_name=None,
            created_at=date(2026, 1, 16),
        )

        expense3 = BudgetExpense(
            id=None,
            budget_id=2,  # Different budget
            purchase_id=2,
            installment_id=None,
            paid_by_user_id=1,
            split_type=SplitType.EQUAL,
            amount=Money(Decimal("200.00"), "ARS"),
            currency="ARS",
            description="Expense 3",
            date=date(2026, 1, 17),
            payment_method_name=None,
            created_at=date(2026, 1, 17),
        )

        saved_expense1 = budget_repo.save(expense1)
        saved_expense2 = budget_repo.save(expense2)
        saved_expense3 = budget_repo.save(expense3)

        # Create responsibilities
        responsibility1 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=saved_expense1.id,
            user_id=1,
            percentage=Decimal("50.00"),
            responsible_amount=Money(Decimal("500.00"), "ARS"),
        )

        responsibility2 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=saved_expense1.id,
            user_id=2,
            percentage=Decimal("50.00"),
            responsible_amount=Money(Decimal("500.00"), "ARS"),
        )

        responsibility3 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=saved_expense2.id,
            user_id=1,
            percentage=Decimal("100.00"),
            responsible_amount=Money(Decimal("500.00"), "ARS"),
        )

        responsibility4 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=saved_expense3.id,  # Different budget
            user_id=1,
            percentage=Decimal("100.00"),
            responsible_amount=Money(Decimal("200.00"), "ARS"),
        )

        repo.save(responsibility1)
        repo.save(responsibility2)
        repo.save(responsibility3)
        repo.save(responsibility4)

        # Find responsibilities for budget 1
        budget_1_responsibilities = repo.find_by_budget_id(1)
        assert isinstance(budget_1_responsibilities, dict)
        assert len(budget_1_responsibilities) == 2  # Two expenses in budget 1

        # Check expense 1 has 2 responsibilities
        assert saved_expense1.id in budget_1_responsibilities
        assert len(budget_1_responsibilities[saved_expense1.id]) == 2
        user_ids_expense1 = [r.user_id for r in budget_1_responsibilities[saved_expense1.id]]
        assert 1 in user_ids_expense1
        assert 2 in user_ids_expense1

        # Check expense 2 has 1 responsibility
        assert saved_expense2.id in budget_1_responsibilities
        assert len(budget_1_responsibilities[saved_expense2.id]) == 1
        assert budget_1_responsibilities[saved_expense2.id][0].user_id == 1

        # Find responsibilities for budget 2
        budget_2_responsibilities = repo.find_by_budget_id(2)
        assert isinstance(budget_2_responsibilities, dict)
        assert len(budget_2_responsibilities) == 1  # One expense in budget 2
        assert saved_expense3.id in budget_2_responsibilities
        assert len(budget_2_responsibilities[saved_expense3.id]) == 1

        # Find responsibilities for non-existent budget
        empty_responsibilities = repo.find_by_budget_id(999)
        assert isinstance(empty_responsibilities, dict)
        assert len(empty_responsibilities) == 0

    def test_save_many(self, db_session):
        """Test saving multiple responsibilities at once"""
        repo = SQLAlchemyBudgetExpenseResponsibilityRepository(db_session)

        responsibilities = [
            BudgetExpenseResponsibility(
                id=None,
                budget_expense_id=1,
                user_id=1,
                percentage=Decimal("40.00"),
                responsible_amount=Money(Decimal("400.00"), "ARS"),
            ),
            BudgetExpenseResponsibility(
                id=None,
                budget_expense_id=1,
                user_id=2,
                percentage=Decimal("60.00"),
                responsible_amount=Money(Decimal("600.00"), "ARS"),
            ),
        ]

        # Save many
        saved_responsibilities = repo.save_many(responsibilities)
        assert len(saved_responsibilities) == 2
        assert all(r.id is not None for r in saved_responsibilities)
        assert saved_responsibilities[0].budget_expense_id == 1
        assert saved_responsibilities[1].budget_expense_id == 1
        assert saved_responsibilities[0].user_id == 1
        assert saved_responsibilities[1].user_id == 2

    def test_update_responsibility(self, db_session):
        """Test updating an existing responsibility"""
        repo = SQLAlchemyBudgetExpenseResponsibilityRepository(db_session)

        # Create initial responsibility
        responsibility = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("50.00"),
            responsible_amount=Money(Decimal("500.00"), "ARS"),
        )

        saved_responsibility = repo.save(responsibility)
        original_id = saved_responsibility.id

        # Update responsibility
        updated_responsibility = BudgetExpenseResponsibility(
            id=original_id,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("75.00"),  # Changed
            responsible_amount=Money(Decimal("750.00"), "ARS"),  # Changed
        )

        result = repo.save(updated_responsibility)
        assert result.id == original_id
        assert result.percentage == Decimal("75.00")
        assert result.responsible_amount == Money(Decimal("750.00"), "ARS")

        # Verify in database
        found = repo.find_by_id(original_id)
        assert found is not None
        assert found.percentage == Decimal("75.00")
        assert found.responsible_amount == Money(Decimal("750.00"), "ARS")

    def test_delete_responsibility(self, db_session):
        """Test deleting a responsibility"""
        repo = SQLAlchemyBudgetExpenseResponsibilityRepository(db_session)

        responsibility = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("100.00"),
            responsible_amount=Money(Decimal("1000.00"), "ARS"),
        )

        saved_responsibility = repo.save(responsibility)
        responsibility_id = saved_responsibility.id

        # Verify it exists
        found = repo.find_by_id(responsibility_id)
        assert found is not None

        # Delete it
        repo.delete(responsibility_id)

        # Verify it's gone
        found_after_delete = repo.find_by_id(responsibility_id)
        assert found_after_delete is None

    def test_delete_by_budget_expense_id(self, db_session):
        """Test deleting all responsibilities for a budget expense"""
        repo = SQLAlchemyBudgetExpenseResponsibilityRepository(db_session)

        # Create multiple responsibilities for the same budget expense
        responsibility1 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=1,
            user_id=1,
            percentage=Decimal("50.00"),
            responsible_amount=Money(Decimal("500.00"), "ARS"),
        )

        responsibility2 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=1,
            user_id=2,
            percentage=Decimal("50.00"),
            responsible_amount=Money(Decimal("500.00"), "ARS"),
        )

        responsibility3 = BudgetExpenseResponsibility(
            id=None,
            budget_expense_id=2,  # Different budget expense
            user_id=1,
            percentage=Decimal("100.00"),
            responsible_amount=Money(Decimal("200.00"), "ARS"),
        )

        repo.save(responsibility1)
        repo.save(responsibility2)
        repo.save(responsibility3)

        # Verify they exist
        expense_1_responsibilities = repo.find_by_budget_expense_id(1)
        assert len(expense_1_responsibilities) == 2

        expense_2_responsibilities = repo.find_by_budget_expense_id(2)
        assert len(expense_2_responsibilities) == 1

        # Delete all for budget expense 1
        repo.delete_by_budget_expense_id(1)

        # Verify expense 1 responsibilities are gone
        expense_1_after_delete = repo.find_by_budget_expense_id(1)
        assert len(expense_1_after_delete) == 0

        # Verify expense 2 responsibilities still exist
        expense_2_after_delete = repo.find_by_budget_expense_id(2)
        assert len(expense_2_after_delete) == 1