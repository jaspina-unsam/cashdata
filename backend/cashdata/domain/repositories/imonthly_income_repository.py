from abc import ABC, abstractmethod
from typing import List, Optional
from cashdata.domain.entities.monthly_income import MonthlyIncome
from cashdata.domain.value_objects.period import Period


class IMonthlyIncomeRepository(ABC):
    @abstractmethod
    def find_by_id(self, monthly_income_id: int) -> Optional[MonthlyIncome]:
        """Retrieve monthly income by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[MonthlyIncome]:
        """Retrieve all incomes"""
        pass

    @abstractmethod
    def find_all_from_user(self, user_id: int) -> List[MonthlyIncome]:
        """Retrieve all incomes from a given user"""
        pass

    @abstractmethod
    def find_by_user_and_period(
        self, user_id: int, period: Period
    ) -> Optional[MonthlyIncome]:
        """Buscar income de UN usuario en UN periodo"""
        pass

    @abstractmethod
    def find_by_period(self, period: Period) -> List[MonthlyIncome]:
        """Buscar TODOS los incomes de un periodo (crítico para ApportionmentCalculator)"""
        pass

    @abstractmethod
    def save(self, monthly_income: MonthlyIncome) -> MonthlyIncome:
        """Insert or update monthly income"""
        pass

    @abstractmethod
    def delete(self, monthly_income_id: int) -> bool:
        """Delete monthly income by ID"""
        pass
