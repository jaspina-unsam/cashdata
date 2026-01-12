from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.domain.entities.budget_expense_responsibility import BudgetExpenseResponsibility
from app.domain.repositories.ibudget_expense_responsibility_repository import IBudgetExpenseResponsibilityRepository
from app.infrastructure.persistence.mappers.budget_expense_responsibility_mapper import BudgetExpenseResponsibilityMapper
from app.infrastructure.persistence.models.budget_expense_responsibility_model import BudgetExpenseResponsibilityModel


class SQLAlchemyBudgetExpenseResponsibilityRepository(IBudgetExpenseResponsibilityRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, responsibility_id: int) -> Optional[BudgetExpenseResponsibility]:
        """Retrieve budget expense responsibility by ID"""
        responsibility = self.session.scalars(
            select(BudgetExpenseResponsibilityModel).where(BudgetExpenseResponsibilityModel.id == responsibility_id)
        ).first()
        return BudgetExpenseResponsibilityMapper.to_entity(responsibility) if responsibility else None

    def find_by_budget_expense_id(self, budget_expense_id: int) -> List[BudgetExpenseResponsibility]:
        """Find all responsibilities for a specific budget expense"""
        responsibilities = self.session.scalars(
            select(BudgetExpenseResponsibilityModel).where(BudgetExpenseResponsibilityModel.budget_expense_id == budget_expense_id)
        ).all()
        return [BudgetExpenseResponsibilityMapper.to_entity(r) for r in responsibilities]

    def find_by_user_id(self, user_id: int) -> List[BudgetExpenseResponsibility]:
        """Find all responsibilities for a specific user"""
        responsibilities = self.session.scalars(
            select(BudgetExpenseResponsibilityModel).where(BudgetExpenseResponsibilityModel.user_id == user_id)
        ).all()
        return [BudgetExpenseResponsibilityMapper.to_entity(r) for r in responsibilities]

    def find_by_budget_id(self, budget_id: int) -> Dict[int, List[BudgetExpenseResponsibility]]:
        """
        Find all responsibilities for a specific budget.
        Returns a dict where key is budget_expense_id and value is list of responsibilities.
        """
        # Join with budget_expenses to filter by budget_id
        from app.infrastructure.persistence.models.budget_expense_model import BudgetExpenseModel

        responsibilities = self.session.scalars(
            select(BudgetExpenseResponsibilityModel)
            .join(BudgetExpenseModel)
            .where(BudgetExpenseModel.budget_id == budget_id)
        ).all()

        # Group by budget_expense_id
        result = {}
        for responsibility in responsibilities:
            expense_id = responsibility.budget_expense_id
            if expense_id not in result:
                result[expense_id] = []
            result[expense_id].append(BudgetExpenseResponsibilityMapper.to_entity(responsibility))

        return result

    def save(self, responsibility: BudgetExpenseResponsibility) -> BudgetExpenseResponsibility:
        """Insert or update budget expense responsibility"""
        if responsibility.id is not None:
            # Update existing
            existing = self.session.get(BudgetExpenseResponsibilityModel, responsibility.id)
            if existing:
                existing.budget_expense_id = responsibility.budget_expense_id
                existing.user_id = responsibility.user_id
                existing.percentage = responsibility.percentage
                existing.responsible_amount = responsibility.responsible_amount.amount
                existing.responsible_currency = responsibility.responsible_amount.currency
                self.session.flush()
                self.session.refresh(existing)
                return BudgetExpenseResponsibilityMapper.to_entity(existing)

        # Insert new
        model = BudgetExpenseResponsibilityMapper.to_model(responsibility)
        merged_model = self.session.merge(model)
        self.session.flush()
        self.session.refresh(merged_model)
        return BudgetExpenseResponsibilityMapper.to_entity(merged_model)

    def save_many(self, responsibilities: List[BudgetExpenseResponsibility]) -> List[BudgetExpenseResponsibility]:
        """Insert or update multiple budget expense responsibilities"""
        result = []
        for responsibility in responsibilities:
            saved = self.save(responsibility)
            result.append(saved)
        return result

    def delete(self, responsibility_id: int) -> None:
        """Delete budget expense responsibility by ID"""
        self.session.execute(
            delete(BudgetExpenseResponsibilityModel).where(BudgetExpenseResponsibilityModel.id == responsibility_id)
        )

    def delete_by_budget_expense_id(self, budget_expense_id: int) -> None:
        """Delete all responsibilities for a specific budget expense"""
        self.session.execute(
            delete(BudgetExpenseResponsibilityModel).where(BudgetExpenseResponsibilityModel.budget_expense_id == budget_expense_id)
        )