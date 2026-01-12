from typing import List

from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.value_objects.period import Period
from app.application.dtos.monthly_budget_dto import MonthlyBudgetResponseDTO
from app.application.mappers.monthly_budget_dto_mapper import MonthlyBudgetDTOMapper


class ListBudgetsByPeriodUseCase:
    """Use case for listing budgets by period that user participates in"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, period_str: str, user_id: int) -> List[MonthlyBudgetResponseDTO]:
        """
        List all budgets for a specific period where user is a participant

        Args:
            period_str: Period in YYYYMM format
            user_id: ID of the user to filter budgets

        Returns:
            List[MonthlyBudgetResponseDTO]: List of budgets with participant counts
        """
        with self._uow:
            # 1. Parse and validate period
            try:
                period = Period.from_string(period_str)
            except Exception:
                # Return empty list for invalid periods
                return []

            # 2. Find budgets for the period
            period_budgets = self._uow.monthly_budgets.find_by_period(period_str)

            # 3. Filter budgets where user is a participant
            user_budgets = []
            for budget in period_budgets:
                is_participant = self._uow.budget_participants.find_by_budget_and_user(budget.id, user_id)
                if is_participant:
                    # Get participant count for this budget
                    participants = self._uow.budget_participants.find_by_budget_id(budget.id)
                    participant_count = len(participants)
                    user_budgets.append((budget, participant_count))

        # 4. Map to response DTOs
        return [
            MonthlyBudgetDTOMapper.to_response_dto(budget, count)
            for budget, count in user_budgets
        ]