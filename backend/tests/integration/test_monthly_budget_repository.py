import pytest
from datetime import datetime
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.value_objects.budget_status import BudgetStatus
from app.infrastructure.persistence.repositories.sqlalchemy_monthly_budget_repository import SQLAlchemyMonthlyBudgetRepository


class TestMonthlyBudgetRepository:
    def test_save_and_find_by_id(self, db_session):
        """Test saving and retrieving a monthly budget"""
        repo = SQLAlchemyMonthlyBudgetRepository(db_session)

        budget = MonthlyBudget(
            id=None,
            name="Test Budget",
            description="Test budget description",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=datetime(2026, 1, 1, 12, 0, 0),
            updated_at=None
        )

        # Save budget
        saved_budget = repo.save(budget)
        assert saved_budget.id is not None
        assert saved_budget.name == "Test Budget"
        assert saved_budget.status == BudgetStatus.ACTIVE

        # Find by ID
        found_budget = repo.find_by_id(saved_budget.id)
        assert found_budget is not None
        assert found_budget.id == saved_budget.id
        assert found_budget.name == "Test Budget"

    def test_save_budget_with_creator(self, db_session):
        """Test saving budget by creator"""
        repo = SQLAlchemyMonthlyBudgetRepository(db_session)

        budget = MonthlyBudget(
            id=None,
            name="Creator Budget",
            description="Budget by creator",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=2,
            created_at=datetime(2026, 2, 1, 12, 0, 0),
            updated_at=None
        )

        saved_budget = repo.save(budget)
        assert saved_budget.id is not None
        assert saved_budget.name == "Creator Budget"
        assert saved_budget.created_by_user_id == 2

    def test_find_by_period(self, db_session):
        """Test finding all budgets"""
        repo = SQLAlchemyMonthlyBudgetRepository(db_session)

        # Create multiple budgets
        budget1 = MonthlyBudget(
            id=None,
            name="Budget 1",
            description="First budget",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=datetime(2026, 3, 1, 12, 0, 0),
            updated_at=None
        )

        budget2 = MonthlyBudget(
            id=None,
            name="Budget 2",
            description="Second budget",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=2,
            created_at=datetime(2026, 3, 2, 12, 0, 0),
            updated_at=None
        )

        repo.save(budget1)
        repo.save(budget2)

        # Find all budgets
        budgets = repo.find_all()
        assert len(budgets) >= 2
        budget_names = [b.name for b in budgets]
        assert "Budget 1" in budget_names
        assert "Budget 2" in budget_names

    def test_update_budget(self, db_session):
        """Test updating an existing budget"""
        repo = SQLAlchemyMonthlyBudgetRepository(db_session)

        budget = MonthlyBudget(
            id=None,
            name="Original Name",
            description="Original description",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=datetime(2026, 4, 1, 12, 0, 0),
            updated_at=None
        )

        saved_budget = repo.save(budget)

        # Update budget
        updated_budget = MonthlyBudget(
            id=saved_budget.id,
            name="Updated Name",
            description="Updated description",
            status=BudgetStatus.CLOSED,
            created_by_user_id=1,
            created_at=saved_budget.created_at,
            updated_at=datetime(2026, 4, 2, 12, 0, 0)
        )

        result = repo.save(updated_budget)

        # Verify update
        assert result.id == saved_budget.id
        assert result.name == "Updated Name"
        assert result.description == "Updated description"
        assert result.status == BudgetStatus.CLOSED
        assert result.updated_at == datetime(2026, 4, 2, 12, 0, 0)

    def test_delete_budget(self, db_session):
        """Test deleting a budget"""
        repo = SQLAlchemyMonthlyBudgetRepository(db_session)

        budget = MonthlyBudget(
            id=None,
            name="Budget to Delete",
            description="Will be deleted",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=datetime(2026, 5, 1, 12, 0, 0),
            updated_at=None
        )

        saved_budget = repo.save(budget)

        # Delete budget
        repo.delete(saved_budget.id)

        # Verify deletion
        found_budget = repo.find_by_id(saved_budget.id)
        assert found_budget is None

    def test_find_by_user_participant(self, db_session):
        """Test finding budgets where user is a participant"""
        from app.infrastructure.persistence.repositories.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
        from app.domain.entities.budget_participant import BudgetParticipant

        # Create budgets
        budget1 = MonthlyBudget(
            id=None,
            name="Budget 1",
            description="Budget for user 1",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=datetime(2026, 6, 1, 12, 0, 0),
            updated_at=None
        )

        budget2 = MonthlyBudget(
            id=None,
            name="Budget 2",
            description="Budget for user 1 and 2",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=2,
            created_at=datetime(2026, 6, 1, 12, 0, 0),
            updated_at=None
        )

        budget3 = MonthlyBudget(
            id=None,
            name="Budget 3",
            description="Budget for user 2 only",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=2,
            created_at=datetime(2026, 6, 1, 12, 0, 0),
            updated_at=None
        )

        # Save budgets using UnitOfWork
        with SQLAlchemyUnitOfWork(lambda: db_session) as uow:
            budget1 = uow.monthly_budgets.save(budget1)
            budget2 = uow.monthly_budgets.save(budget2)
            budget3 = uow.monthly_budgets.save(budget3)

            # Create participants
            participant1 = BudgetParticipant(id=None, budget_id=budget1.id, user_id=1)
            participant2 = BudgetParticipant(id=None, budget_id=budget2.id, user_id=1)
            participant3 = BudgetParticipant(id=None, budget_id=budget2.id, user_id=2)
            participant4 = BudgetParticipant(id=None, budget_id=budget3.id, user_id=2)

            uow.budget_participants.save_many([participant1, participant2, participant3, participant4])
            uow.commit()

        # Test find_by_user_participant
        repo = SQLAlchemyMonthlyBudgetRepository(db_session)

        # Find budgets for user 1
        user_1_budgets = repo.find_by_user_participant(1)
        assert len(user_1_budgets) == 2

        budget_ids = [b.id for b in user_1_budgets]
        assert budget1.id in budget_ids
        assert budget2.id in budget_ids

        # Find budgets for user 2
        user_2_budgets = repo.find_by_user_participant(2)
        assert len(user_2_budgets) == 2

        budget_ids = [b.id for b in user_2_budgets]
        assert budget2.id in budget_ids
        assert budget3.id in budget_ids

        # Find budgets for user with no participations
        empty_budgets = repo.find_by_user_participant(999)
        assert len(empty_budgets) == 0