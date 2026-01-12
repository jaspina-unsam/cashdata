from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.entities.budget_expense import BudgetExpense
from app.domain.entities.budget_expense_responsibility import BudgetExpenseResponsibility
from app.application.dtos.monthly_budget_dto import MonthlyBudgetResponseDTO
from app.application.mappers.monthly_budget_dto_mapper import MonthlyBudgetDTOMapper
from app.application.exceptions.application_exceptions import BusinessRuleViolationError


class GetBudgetDetailsUseCase:
    """Use case for getting complete budget details with expenses and balances"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, budget_id: int, requesting_user_id: int) -> MonthlyBudgetResponseDTO:
        """
        Get complete budget details including expenses and participant count

        Args:
            budget_id: ID of the budget to retrieve
            requesting_user_id: ID of the user making the request (for authorization)

        Returns:
            MonthlyBudgetResponseDTO: Complete budget data

        Raises:
            BusinessRuleViolationError: If budget not found or user not authorized
        """
        with self._uow:
            # 1. Find budget
            budget = self._uow.monthly_budgets.find_by_id(budget_id)
            if not budget:
                raise BusinessRuleViolationError(f"Budget with ID {budget_id} not found")

            # 2. Check if requesting user is a participant
            is_participant = self._uow.budget_participants.find_by_budget_and_user(budget_id, requesting_user_id)
            if not is_participant:
                raise BusinessRuleViolationError(f"User {requesting_user_id} is not authorized to view budget {budget_id}")

            # 3. Get participant count
            participants = self._uow.budget_participants.find_by_budget_id(budget_id)
            participant_count = len(participants)

        # 4. Return budget details with participant count
        return MonthlyBudgetDTOMapper.to_response_dto(budget, participant_count)