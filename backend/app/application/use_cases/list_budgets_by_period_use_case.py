from typing import List

from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.application.dtos.monthly_budget_dto import MonthlyBudgetResponseDTO
from app.application.mappers.monthly_budget_dto_mapper import MonthlyBudgetDTOMapper


class ListBudgetsUseCase:
    """Use case for listing all budgets that user participates in"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, user_id: int) -> List[MonthlyBudgetResponseDTO]:
        """
        List all budgets where user is a participant, ordered by created_at DESC

        Args:
            user_id: ID of the user to filter budgets

        Returns:
            List[MonthlyBudgetResponseDTO]: List of budgets with participant counts
        """
        with self._uow:
            # 1. Find budgets where user is a participant (already sorted by created_at DESC in repository)
            user_budgets = self._uow.monthly_budgets.find_by_user_participant(user_id)

            # 2. Get participant counts for each budget
            budgets_with_counts = []
            for budget in user_budgets:
                participants = self._uow.budget_participants.find_by_budget_id(budget.id)
                participant_count = len(participants)
                budgets_with_counts.append((budget, participant_count))

        # 3. Map to response DTOs
        return [
            MonthlyBudgetDTOMapper.to_response_dto(budget, count)
            for budget, count in budgets_with_counts
        ]