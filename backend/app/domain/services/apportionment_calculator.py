from typing import List, Dict
from decimal import Decimal
from app.domain.entities.user import User
from app.domain.entities.monthly_income import MonthlyIncome
from app.domain.value_objects.period import Period
from app.domain.value_objects.percentage import Percentage
from app.domain.exceptions.domain_exceptions import InvalidCalculation


class ApportionmentCalculator:
    """
    Domain Service to split expenses.

    Calculates percentages based on monthly income.
    If there are no incomes set, equal split is applied.
    """

    def calculate_percentages(
        self, users: List[User], incomes: List[MonthlyIncome], period: Period
    ) -> Dict[int, Percentage]:
        if not users:
            raise InvalidCalculation("At least one user is required")

        if users is None or incomes is None:
            raise InvalidCalculation("Users and incomes cannot be None")

        period_incomes = [inc for inc in incomes if inc.period == period]

        if period_incomes and len({inc.amount.currency for inc in period_incomes}) > 1:
            raise InvalidCalculation("All incomes must be in the same currency")

        total = sum(inc.amount.amount for inc in period_incomes)

        if not period_incomes or total == Decimal("0"):
            equal_percentage = Percentage(Decimal("100") / Decimal(str(len(users))))
            return {user.id: equal_percentage for user in users}

        percentages = {}
        for user in users:
            user_income = next(
                (inc for inc in period_incomes if inc.user_id == user.id), None
            )
            if user_income:
                proportion = user_income.amount.amount / total
                percentages[user.id] = Percentage.from_decimal(proportion)
            else:
                percentages[user.id] = Percentage(Decimal("0"))

        return percentages
