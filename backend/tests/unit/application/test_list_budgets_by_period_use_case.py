import pytest
from unittest.mock import Mock

from app.application.use_cases.list_budgets_by_period_use_case import ListBudgetsUseCase
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.entities.budget_participant import BudgetParticipant
from app.domain.value_objects.budget_status import BudgetStatus


@pytest.fixture
def mock_unit_of_work():
    uow = Mock()
    uow.monthly_budgets = Mock()
    uow.budget_participants = Mock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


class TestListBudgetsUseCase:

    def test_should_return_budgets_where_user_is_participant(self, mock_unit_of_work):
        """
        GIVEN: Multiple budgets exist, user is participant in some
        WHEN: Execute use case
        THEN: Return only budgets where user is participant with correct counts
        """
        # Arrange
        budget1 = MonthlyBudget(
            id=1,
            name="Budget 1",
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=None,
            updated_at=None,
        )

        budget2 = MonthlyBudget(
            id=2,
            name="Budget 2",
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=2,
            created_at=None,
            updated_at=None,
        )

        budget3 = MonthlyBudget(
            id=3,
            name="Budget 3",
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=None,
            updated_at=None,
        )

        # User 1 is participant in budget1 and budget2
        mock_unit_of_work.monthly_budgets.find_by_user_participant.return_value = [budget1, budget2]

        mock_unit_of_work.budget_participants.find_by_budget_id.side_effect = lambda budget_id: {
            1: [BudgetParticipant(id=1, budget_id=1, user_id=1), BudgetParticipant(id=2, budget_id=1, user_id=2)],
            2: [BudgetParticipant(id=3, budget_id=2, user_id=1)],
        }.get(budget_id, [])

        use_case = ListBudgetsUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(1)

        # Assert
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].participant_count == 2
        assert result[1].id == 2
        assert result[1].participant_count == 1

    def test_should_return_empty_list_when_no_budgets_for_user(self, mock_unit_of_work):
        """
        GIVEN: No budgets exist for the user
        WHEN: Execute use case
        THEN: Return empty list
        """
        # Arrange
        mock_unit_of_work.monthly_budgets.find_by_user_participant.return_value = []

        use_case = ListBudgetsUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(1)

        # Assert
        assert result == []