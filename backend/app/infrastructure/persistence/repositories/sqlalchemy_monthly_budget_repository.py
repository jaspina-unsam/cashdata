from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.repositories.imonthly_budget_repository import IMonthlyBudgetRepository
from app.infrastructure.persistence.mappers.monthly_budget_mapper import MonthlyBudgetMapper
from app.infrastructure.persistence.models.monthly_budget_model import MonthlyBudgetModel


class SQLAlchemyMonthlyBudgetRepository(IMonthlyBudgetRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, budget_id: int) -> Optional[MonthlyBudget]:
        """Retrieve monthly budget by ID"""
        budget = self.session.scalars(
            select(MonthlyBudgetModel).where(MonthlyBudgetModel.id == budget_id)
        ).first()
        return MonthlyBudgetMapper.to_entity(budget) if budget else None

    def find_all(self) -> List[MonthlyBudget]:
        """Find all budgets ordered by created_at DESC"""
        budgets = self.session.scalars(
            select(MonthlyBudgetModel).order_by(MonthlyBudgetModel.created_at.desc())
        ).all()
        return [MonthlyBudgetMapper.to_entity(b) for b in budgets]

    def find_by_user_participant(self, user_id: int) -> List[MonthlyBudget]:
        """Find all budgets where user is a participant"""
        from app.infrastructure.persistence.models.budget_participant_model import BudgetParticipantModel

        budgets = self.session.scalars(
            select(MonthlyBudgetModel)
            .join(BudgetParticipantModel, MonthlyBudgetModel.id == BudgetParticipantModel.budget_id)
            .where(BudgetParticipantModel.user_id == user_id)
            .order_by(MonthlyBudgetModel.created_at.desc())
            .distinct()
        ).all()
        return [MonthlyBudgetMapper.to_entity(b) for b in budgets]

    def save(self, budget: MonthlyBudget) -> MonthlyBudget:
        """Insert or update monthly budget"""
        if budget.id is not None:
            # Update existing
            existing = self.session.get(MonthlyBudgetModel, budget.id)
            if existing:
                existing.name = budget.name
                existing.description = budget.description
                existing.status = budget.status.value
                existing.created_by_user_id = budget.created_by_user_id
                existing.created_at = budget.created_at
                existing.updated_at = budget.updated_at
                self.session.flush()
                self.session.refresh(existing)
                return MonthlyBudgetMapper.to_entity(existing)

        # Insert new
        model = MonthlyBudgetMapper.to_model(budget)
        merged_model = self.session.merge(model)
        self.session.flush()
        self.session.refresh(merged_model)
        return MonthlyBudgetMapper.to_entity(merged_model)

    def delete(self, budget_id: int) -> None:
        """Delete monthly budget by ID"""
        self.session.execute(
            delete(MonthlyBudgetModel).where(MonthlyBudgetModel.id == budget_id)
        )