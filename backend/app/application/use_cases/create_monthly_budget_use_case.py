from datetime import datetime
from typing import List

from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.entities.budget_participant import BudgetParticipant
from app.domain.value_objects.budget_status import BudgetStatus
from app.application.dtos.monthly_budget_dto import CreateMonthlyBudgetCommand, MonthlyBudgetResponseDTO
from app.application.mappers.monthly_budget_dto_mapper import MonthlyBudgetDTOMapper
from app.application.exceptions.application_exceptions import (
    UserNotFoundError,
    BusinessRuleViolationError,
)


class CreateMonthlyBudgetUseCase:
    """Use case for creating a new monthly budget with participants"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, command: CreateMonthlyBudgetCommand) -> MonthlyBudgetResponseDTO:
        """
        Create a new monthly budget with participants

        Args:
            command: Validated budget creation data

        Returns:
            MonthlyBudgetResponseDTO: Created budget data with participant count

        Raises:
            UserNotFoundError: If creator or any participant doesn't exist
            BusinessRuleViolationError: If creator is not a participant or duplicate participants
        """
        with self._uow:
            # 1. Validate that creator exists
            creator = self._uow.users.find_by_id(command.created_by_user_id)
            if not creator:
                raise UserNotFoundError(f"Creator user with ID {command.created_by_user_id} not found")

            # 2. Validate that all participants exist
            participant_users = []
            for user_id in command.participant_user_ids:
                user = self._uow.users.find_by_id(user_id)
                if not user:
                    raise UserNotFoundError(f"Participant user with ID {user_id} not found")
                participant_users.append(user)

            # 3. Validate that creator is a participant
            if command.created_by_user_id not in command.participant_user_ids:
                raise BusinessRuleViolationError("Budget creator must be a participant")

            # 4. Validate no duplicate participants
            if len(command.participant_user_ids) != len(set(command.participant_user_ids)):
                raise BusinessRuleViolationError("Duplicate participant user IDs are not allowed")

            # 5. Create MonthlyBudget entity
            budget = MonthlyBudget(
                id=None,
                name=command.name,
                description=command.description,
                status=BudgetStatus.ACTIVE,
                created_by_user_id=command.created_by_user_id,
                created_at=datetime.now(),
                updated_at=None,
            )

            # 6. Save budget
            saved_budget = self._uow.monthly_budgets.save(budget)

            # 7. Create and save participants
            participants = [
                BudgetParticipant(id=None, budget_id=saved_budget.id, user_id=user_id)
                for user_id in command.participant_user_ids
            ]
            saved_participants = self._uow.budget_participants.save_many(participants)

            # 8. Commit transaction
            self._uow.commit()

        # 9. Return response DTO with participant count
        return MonthlyBudgetDTOMapper.to_response_dto(saved_budget, len(saved_participants))