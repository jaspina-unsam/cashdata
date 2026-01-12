import pytest
from unittest.mock import Mock

from app.application.use_cases.get_budget_details_use_case import GetBudgetDetailsUseCase
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.entities.budget_participant import BudgetParticipant
from app.domain.value_objects.period import Period
from app.domain.value_objects.budget_status import BudgetStatus
from app.application.exceptions.application_exceptions import BusinessRuleViolationError


@pytest.fixture
def mock_unit_of_work():
    uow = Mock()
    uow.monthly_budgets = Mock()
    uow.budget_participants = Mock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


class TestGetBudgetDetailsUseCase:

    def test_should_return_budget_details_for_participant(self, mock_unit_of_work):
        """
        GIVEN: Budget exists and user is a participant
        WHEN: Execute use case
        THEN: Return budget details with participant count
        """
        # Arrange
        budget = MonthlyBudget(
            id=1,
            name="Test Budget",
            period=Period(2026, 1),
            description="Test description",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=None,
            updated_at=None,
        )

        participants = [
            BudgetParticipant(id=1, budget_id=1, user_id=1),
            BudgetParticipant(id=2, budget_id=1, user_id=2),
        ]

        mock_unit_of_work.monthly_budgets.find_by_id.return_value = budget
        mock_unit_of_work.budget_participants.find_by_budget_and_user.return_value = participants[1]  # User 2 is participant
        mock_unit_of_work.budget_participants.find_by_budget_id.return_value = participants

        use_case = GetBudgetDetailsUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(1, 2)

        # Assert
        assert result.id == 1
        assert result.name == "Test Budget"
        assert result.participant_count == 2

        mock_unit_of_work.monthly_budgets.find_by_id.assert_called_once_with(1)
        mock_unit_of_work.budget_participants.find_by_budget_and_user.assert_called_once_with(1, 2)
        mock_unit_of_work.budget_participants.find_by_budget_id.assert_called_once_with(1)

    def test_should_fail_when_budget_not_found(self, mock_unit_of_work):
        """
        GIVEN: Budget does not exist
        WHEN: Execute use case
        THEN: BusinessRuleViolationError is raised
        """
        # Arrange
        mock_unit_of_work.monthly_budgets.find_by_id.return_value = None

        use_case = GetBudgetDetailsUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(BusinessRuleViolationError, match="Budget with ID 1 not found"):
            use_case.execute(1, 2)

    def test_should_fail_when_user_not_participant(self, mock_unit_of_work):
        """
        GIVEN: Budget exists but user is not a participant
        WHEN: Execute use case
        THEN: BusinessRuleViolationError is raised
        """
        # Arrange
        budget = MonthlyBudget(
            id=1,
            name="Test Budget",
            period=Period(2026, 1),
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=None,
            updated_at=None,
        )

        mock_unit_of_work.monthly_budgets.find_by_id.return_value = budget
        mock_unit_of_work.budget_participants.find_by_budget_and_user.return_value = None  # User not participant

        use_case = GetBudgetDetailsUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(BusinessRuleViolationError, match="User 3 is not authorized to view budget 1"):
            use_case.execute(1, 3)