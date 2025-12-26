from dataclasses import dataclass
from enum import StrEnum

from cashdata.domain.value_objects.money import Money
from cashdata.domain.value_objects.period import Period


class IncomeSource(StrEnum):
    WAGE = "WAGE"
    FREELANCE = "FREELANCE"
    OTHER = "OTHER"


@dataclass
class MonthlyIncome:
    id: int
    user_id: int
    period: Period
    amount: Money
    source: IncomeSource = IncomeSource.WAGE

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: "MonthlyIncome") -> bool:
        if not isinstance(other, MonthlyIncome):
            return False

        return self.id == other.id

    def update_amount(self, new_amount: Money) -> None:
        if not isinstance(new_amount, Money):
            raise TypeError(f"Cannot set {new_amount.__class__} as amount")

        self.amount = new_amount

    def update_source(self, new_source: IncomeSource) -> None:
        if not isinstance(new_source, IncomeSource):
            raise TypeError(f"Cannot set {new_source.__class__} as income source")

        self.source = new_source

    def update_period(self, new_period: Period) -> None:
        if not isinstance(new_period, Period):
            raise TypeError(f"Cannot set {new_period.__class__} as period")

        self.period = new_period

    def __str__(self) -> str:
        return f"MonthlyIncome({self.period}, {self.amount}, {self.source})"
