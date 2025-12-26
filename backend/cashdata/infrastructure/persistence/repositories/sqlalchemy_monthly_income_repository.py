from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from cashdata.domain.entities import MonthlyIncome
from cashdata.domain.value_objects import Period
from cashdata.domain.repositories import IMonthlyIncomeRepository
from cashdata.infrastructure.persistence.mappers import MonthlyIncomeMapper
from cashdata.infrastructure.persistence.models import MonthlyIncomeModel


class SQLAlchemyMonthlyIncomeRepository(IMonthlyIncomeRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, monthly_income_id: int) -> Optional[MonthlyIncome]:
        """Retrieve monthly income by ID"""
        monthly_income = self.session.get(MonthlyIncomeModel, monthly_income_id)
        return MonthlyIncomeMapper.to_entity(monthly_income) if monthly_income else None

    def find_all(self) -> List[MonthlyIncome]:
        """Retrieve all incomes"""
        incomes = self.session.scalars(select(MonthlyIncomeModel)).all()
        return [MonthlyIncomeMapper.to_entity(mi) for mi in incomes]

    def find_all_from_user(self, user_id: int) -> List[MonthlyIncome]:
        """Retrieve all incomes from a given user"""
        incomes = self.session.scalars(
            select(MonthlyIncomeModel).where(MonthlyIncomeModel.user_id == user_id)
        ).all()
        return [MonthlyIncomeMapper.to_entity(mi) for mi in incomes]

    def find_by_user_and_period(
        self, user_id: int, period: Period
    ) -> Optional[MonthlyIncome]:
        """Retrieve income for specific user and period"""
        income = self.session.scalars(
            select(MonthlyIncomeModel).where(
                MonthlyIncomeModel.user_id == user_id,
                MonthlyIncomeModel.period_year == period.year,
                MonthlyIncomeModel.period_month == period.month,
            )
        ).first()

        return MonthlyIncomeMapper.to_entity(income) if income else None

    def find_by_period(self, period: Period) -> List[MonthlyIncome]:
        """Retrieve all incomes for a specific period"""
        incomes = self.session.scalars(
            select(MonthlyIncomeModel).where(
                MonthlyIncomeModel.period_year == period.year,
                MonthlyIncomeModel.period_month == period.month,
            )
        ).all()

        return [MonthlyIncomeMapper.to_entity(mi) for mi in incomes]

    def save(self, monthly_income: MonthlyIncome) -> MonthlyIncome:
        """Insert or update monthly income"""
        model = MonthlyIncomeMapper.to_model(monthly_income)
        merged_model = self.session.merge(model)
        self.session.commit()
        self.session.refresh(merged_model)
        return MonthlyIncomeMapper.to_entity(merged_model)

    def delete(self, monthly_income_id: int) -> bool:
        """Delete monthly income by ID"""
        income = self.session.get(MonthlyIncomeModel, monthly_income_id)
        if not income:
            return False

        self.session.delete(income)
        self.session.commit()
        return True
