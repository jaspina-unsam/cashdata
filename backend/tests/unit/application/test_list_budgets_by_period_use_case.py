import pytest
from unittest.mock import Mock

from app.application.use_cases.list_budgets_by_period_use_case import ListBudgetsByPeriodUseCase
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.entities.budget_participant import BudgetParticipant
from app.domain.value_objects.period import Period
from app.domain.value_objects.budget_status import BudgetStatus


@pytest.fixture
def mock_unit_of_work():
    uow = Mock()
    uow.monthly_budgets = Mock()
    uow.budget_participants = Mock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


class TestListBudgetsByPeriodUseCase:

    def test_should_return_budgets_where_user_is_participant(self, mock_unit_of_work):
        """
        GIVEN: Multiple budgets exist for period, user is participant in some
        WHEN: Execute use case
        THEN: Return only budgets where user is participant with correct counts
        """
        # Arrange
        budget1 = MonthlyBudget(
            id=1,
            name="Budget 1",
            period=Period(2026, 1),
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=None,
            updated_at=None,
        )

        budget2 = MonthlyBudget(
            id=2,
            name="Budget 2",
            period=Period(2026, 1),
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=2,
            created_at=None,
            updated_at=None,
        )

        budget3 = MonthlyBudget(
            id=3,
            name="Budget 3",
            period=Period(2026, 2),  # Different period
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=None,
            updated_at=None,
        )

        # User 1 is participant in budget1 and budget2
        mock_unit_of_work.monthly_budgets.find_by_period.side_effect = lambda period: {
            "202601": [budget1, budget2],
            "202602": [budget3]
        }.get(period, [])

        mock_unit_of_work.budget_participants.find_by_budget_and_user.side_effect = lambda budget_id, user_id: {
            (1, 1): BudgetParticipant(id=1, budget_id=1, user_id=1),  # User 1 in budget 1
            (2, 1): BudgetParticipant(id=2, budget_id=2, user_id=1),  # User 1 in budget 2
            (3, 1): None,  # User 1 not in budget 3
        }.get((budget_id, user_id))

        mock_unit_of_work.budget_participants.find_by_budget_id.side_effect = lambda budget_id: {
            1: [BudgetParticipant(id=1, budget_id=1, user_id=1), BudgetParticipant(id=2, budget_id=1, user_id=2)],
            2: [BudgetParticipant(id=3, budget_id=2, user_id=1)],
        }.get(budget_id, [])

        use_case = ListBudgetsByPeriodUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute("202601", 1)

        # Assert
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].participant_count == 2
        assert result[1].id == 2
        assert result[1].participant_count == 1

    def test_should_return_empty_list_when_no_budgets_for_period(self, mock_unit_of_work):
        """
        GIVEN: No budgets exist for the period
        WHEN: Execute use case
        THEN: Return empty list
        """
        # Arrange
        mock_unit_of_work.monthly_budgets.find_by_period.return_value = []

        use_case = ListBudgetsByPeriodUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute("202601", 1)

        # Assert
        assert result == []

    def test_should_return_empty_list_when_user_not_participant_in_any_budget(self, mock_unit_of_work):
        """
        GIVEN: Budgets exist for period but user is not participant in any
        WHEN: Execute use case
        THEN: Return empty list
        """
        # Arrange
        budget = MonthlyBudget(
            id=1,
            name="Budget 1",
            period=Period(2026, 1),
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=2,
            created_at=None,
            updated_at=None,
        )

        mock_unit_of_work.monthly_budgets.find_by_period.return_value = [budget]
        mock_unit_of_work.budget_participants.find_by_budget_and_user.return_value = None  # User not participant

        use_case = ListBudgetsByPeriodUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute("202601", 1)

        # Assert
        assert result == []

    def test_should_return_empty_list_for_invalid_period(self, mock_unit_of_work):
        """
        GIVEN: Invalid period format
        WHEN: Execute use case
        THEN: Return empty list (graceful handling)
        """
        # Arrange
        mock_unit_of_work.monthly_budgets.find_by_period.return_value = []

        use_case = ListBudgetsByPeriodUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute("invalid", 1)

        # Assert
        assert result == []