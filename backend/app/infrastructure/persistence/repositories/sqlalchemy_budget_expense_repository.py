from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.domain.entities.budget_expense import BudgetExpense
from app.domain.repositories.ibudget_expense_repository import IBudgetExpenseRepository
from app.infrastructure.persistence.mappers.budget_expense_mapper import BudgetExpenseMapper
from app.infrastructure.persistence.models.budget_expense_model import BudgetExpenseModel


class SQLAlchemyBudgetExpenseRepository(IBudgetExpenseRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, expense_id: int) -> Optional[BudgetExpense]:
        """Retrieve budget expense by ID"""
        expense = self.session.scalars(
            select(BudgetExpenseModel).where(BudgetExpenseModel.id == expense_id)
        ).first()
        return BudgetExpenseMapper.to_entity(expense) if expense else None

    def find_by_budget_id(self, budget_id: int) -> List[BudgetExpense]:
        """Find all expenses for a specific budget"""
        expenses = self.session.scalars(
            select(BudgetExpenseModel).where(BudgetExpenseModel.budget_id == budget_id)
        ).all()
        return [BudgetExpenseMapper.to_entity(e) for e in expenses]

    def find_by_purchase_id(self, purchase_id: int) -> List[BudgetExpense]:
        """Find all expenses associated with a specific purchase"""
        expenses = self.session.scalars(
            select(BudgetExpenseModel).where(BudgetExpenseModel.purchase_id == purchase_id)
        ).all()
        return [BudgetExpenseMapper.to_entity(e) for e in expenses]

    def find_by_installment_id(self, installment_id: int) -> List[BudgetExpense]:
        """Find all expenses associated with a specific installment"""
        expenses = self.session.scalars(
            select(BudgetExpenseModel).where(BudgetExpenseModel.installment_id == installment_id)
        ).all()
        return [BudgetExpenseMapper.to_entity(e) for e in expenses]

    def find_by_paid_by_user_id(self, user_id: int) -> List[BudgetExpense]:
        """Find all expenses paid by a specific user"""
        expenses = self.session.scalars(
            select(BudgetExpenseModel).where(BudgetExpenseModel.paid_by_user_id == user_id)
        ).all()
        return [BudgetExpenseMapper.to_entity(e) for e in expenses]

    def save(self, expense: BudgetExpense) -> BudgetExpense:
        """Insert or update budget expense"""
        if expense.id is not None:
            # Update existing
            existing = self.session.get(BudgetExpenseModel, expense.id)
            if existing:
                existing.budget_id = expense.budget_id
                existing.purchase_id = expense.purchase_id
                existing.installment_id = expense.installment_id
                existing.paid_by_user_id = expense.paid_by_user_id
                existing.split_type = expense.split_type.value
                existing.amount = expense.amount.amount
                existing.currency = expense.currency
                existing.description = expense.description
                existing.date = expense.date
                existing.payment_method_name = expense.payment_method_name
                existing.created_at = expense.created_at
                self.session.flush()
                self.session.refresh(existing)
                return BudgetExpenseMapper.to_entity(existing)

        # Insert new
        model = BudgetExpenseMapper.to_model(expense)
        merged_model = self.session.merge(model)
        self.session.flush()
        self.session.refresh(merged_model)
        return BudgetExpenseMapper.to_entity(merged_model)

    def delete(self, expense_id: int) -> None:
        """Delete budget expense by ID"""
        expense = self.session.get(BudgetExpenseModel, expense_id)
        if expense:
            self.session.delete(expense)