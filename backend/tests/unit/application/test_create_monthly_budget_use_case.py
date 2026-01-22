import pytest
from datetime import datetime
from unittest.mock import Mock

from app.application.use_cases.create_monthly_budget_use_case import (
    CreateMonthlyBudgetUseCase,
    CreateMonthlyBudgetCommand,
)
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.entities.user import User
from app.domain.entities.budget_participant import BudgetParticipant
from app.domain.value_objects.budget_status import BudgetStatus
from app.domain.value_objects.money import Money, Currency
from app.application.exceptions.application_exceptions import (
    UserNotFoundError,
    BusinessRuleViolationError,
)


@pytest.fixture
def mock_unit_of_work():
    uow = Mock()
    uow.users = Mock()
    uow.monthly_budgets = Mock()
    uow.budget_participants = Mock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


class TestCreateMonthlyBudgetUseCase:

    def test_should_create_budget_with_valid_data(self, mock_unit_of_work):
        """
        GIVEN: Valid budget creation command with creator and participants
        WHEN: Execute use case
        THEN: Budget and participants are created successfully
        """
        # Arrange
        creator = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            wage=Money(50000, Currency.ARS)
        )
        participant = User(
            id=2,
            name="Jane Doe",
            email="jane@example.com",
            wage=Money(45000, Currency.ARS)
        )

        saved_budget = MonthlyBudget(
            id=1,
            name="January 2026 Budget",
            description="Shared budget",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=datetime(2026, 1, 1, 12, 0, 0),
            updated_at=None,
        )

        saved_participants = [
            BudgetParticipant(id=1, budget_id=1, user_id=1),
            BudgetParticipant(id=2, budget_id=1, user_id=2),
        ]

        mock_unit_of_work.users.find_by_id.side_effect = lambda user_id: {
            1: creator,
            2: participant
        }.get(user_id)
        mock_unit_of_work.monthly_budgets.save.return_value = saved_budget
        mock_unit_of_work.budget_participants.save_many.return_value = saved_participants

        command = CreateMonthlyBudgetCommand(
            name="January 2026 Budget",
            description="Shared budget",
            created_by_user_id=1,
            participant_user_ids=[1, 2]
        )
        use_case = CreateMonthlyBudgetUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.id == 1
        assert result.name == "January 2026 Budget"
        assert result.description == "Shared budget"
        assert result.status == "active"
        assert result.created_by_user_id == 1
        assert result.participant_count == 2

        # Verify calls
        mock_unit_of_work.users.find_by_id.assert_any_call(1)
        mock_unit_of_work.users.find_by_id.assert_any_call(2)
        mock_unit_of_work.monthly_budgets.save.assert_called_once()
        mock_unit_of_work.budget_participants.save_many.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_should_create_budget_without_description(self, mock_unit_of_work):
        """
        GIVEN: Valid budget creation command without description
        WHEN: Execute use case
        THEN: Budget is created successfully
        """
        # Arrange
        creator = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            wage=Money(50000, Currency.ARS)
        )

        saved_budget = MonthlyBudget(
            id=1,
            name="January 2026 Budget",
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=datetime(2026, 1, 1, 12, 0, 0),
            updated_at=None,
        )

        saved_participants = [
            BudgetParticipant(id=1, budget_id=1, user_id=1),
        ]

        mock_unit_of_work.users.find_by_id.return_value = creator
        mock_unit_of_work.monthly_budgets.save.return_value = saved_budget
        mock_unit_of_work.budget_participants.save_many.return_value = saved_participants

        command = CreateMonthlyBudgetCommand(
            name="January 2026 Budget",
            description=None,
            created_by_user_id=1,
            participant_user_ids=[1]
        )
        use_case = CreateMonthlyBudgetUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.description is None

    def test_should_fail_when_creator_not_found(self, mock_unit_of_work):
        """
        GIVEN: Creator user does not exist
        WHEN: Execute use case
        THEN: UserNotFoundError is raised
        """
        # Arrange
        mock_unit_of_work.users.find_by_id.return_value = None

        command = CreateMonthlyBudgetCommand(
            name="January 2026 Budget",
            created_by_user_id=1,
            participant_user_ids=[1, 2]
        )
        use_case = CreateMonthlyBudgetUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(UserNotFoundError, match="Creator user with ID 1 not found"):
            use_case.execute(command)

    def test_should_fail_when_participant_not_found(self, mock_unit_of_work):
        """
        GIVEN: One participant user does not exist
        WHEN: Execute use case
        THEN: UserNotFoundError is raised
        """
        # Arrange
        creator = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            wage=Money(50000, Currency.ARS)
        )

        mock_unit_of_work.users.find_by_id.side_effect = lambda user_id: {
            1: creator,
            2: None  # Participant 2 doesn't exist
        }.get(user_id)

        command = CreateMonthlyBudgetCommand(
            name="January 2026 Budget",
            created_by_user_id=1,
            participant_user_ids=[1, 2]
        )
        use_case = CreateMonthlyBudgetUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(UserNotFoundError, match="Participant user with ID 2 not found"):
            use_case.execute(command)

    def test_should_fail_when_creator_not_participant(self, mock_unit_of_work):
        """
        GIVEN: Creator is not included in participants
        WHEN: Execute use case
        THEN: BusinessRuleViolationError is raised
        """
        # Arrange
        creator = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            wage=Money(50000, Currency.ARS)
        )
        participant = User(
            id=2,
            name="Jane Doe",
            email="jane@example.com",
            wage=Money(45000, Currency.ARS)
        )

        mock_unit_of_work.users.find_by_id.side_effect = [creator, participant]

        command = CreateMonthlyBudgetCommand(
            name="January 2026 Budget",
            created_by_user_id=1,
            participant_user_ids=[2]  # Creator not included
        )
        use_case = CreateMonthlyBudgetUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(BusinessRuleViolationError, match="Budget creator must be a participant"):
            use_case.execute(command)

    def test_should_fail_when_duplicate_participants(self, mock_unit_of_work):
        """
        GIVEN: Duplicate participant user IDs
        WHEN: Execute use case
        THEN: BusinessRuleViolationError is raised
        """
        # Arrange
        creator = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            wage=Money(50000, Currency.ARS)
        )

        mock_unit_of_work.users.find_by_id.return_value = creator

        command = CreateMonthlyBudgetCommand(
            name="January 2026 Budget",
            created_by_user_id=1,
            participant_user_ids=[1, 1]  # Duplicate
        )
        use_case = CreateMonthlyBudgetUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(BusinessRuleViolationError, match="Duplicate participant user IDs are not allowed"):
            use_case.execute(command)