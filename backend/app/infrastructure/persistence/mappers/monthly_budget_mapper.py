from datetime import datetime
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.value_objects.period import Period
from app.domain.value_objects.budget_status import BudgetStatus
from app.infrastructure.persistence.models.monthly_budget_model import MonthlyBudgetModel


class MonthlyBudgetMapper:
    @staticmethod
    def to_entity(model: MonthlyBudgetModel) -> MonthlyBudget:
        """SQLAlchemy Model → Domain Entity"""
        return MonthlyBudget(
            id=model.id,
            name=model.name,
            period=Period.from_string(model.period),
            description=model.description,
            status=BudgetStatus(model.status),
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: MonthlyBudget) -> MonthlyBudgetModel:
        """Domain Entity → SQLAlchemy Model"""
        return MonthlyBudgetModel(
            id=entity.id,
            name=entity.name,
            period=entity.period.to_string(),
            description=entity.description,
            status=entity.status.value,
            created_by_user_id=entity.created_by_user_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )