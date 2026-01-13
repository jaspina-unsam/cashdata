from app.domain.entities.monthly_budget import MonthlyBudget
from app.application.dtos.monthly_budget_dto import MonthlyBudgetResponseDTO


class MonthlyBudgetDTOMapper:
    """Maps between MonthlyBudget entity and DTOs"""

    @staticmethod
    def to_response_dto(budget: MonthlyBudget, participant_count: int = 0) -> MonthlyBudgetResponseDTO:
        """Convert domain entity to response DTO"""
        return MonthlyBudgetResponseDTO(
            id=budget.id,
            name=budget.name,
            description=budget.description,
            status=budget.status.value,
            created_by_user_id=budget.created_by_user_id,
            participant_count=participant_count,
            created_at=budget.created_at,
            updated_at=budget.updated_at,
        )