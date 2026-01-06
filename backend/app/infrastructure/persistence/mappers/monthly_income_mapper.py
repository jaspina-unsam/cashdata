from app.domain.entities.monthly_income import MonthlyIncome, IncomeSource
from app.domain.value_objects.money import Money, Currency
from app.domain.value_objects.period import Period
from app.infrastructure.persistence.models.monthly_income_model import MonthlyIncomeModel
from decimal import Decimal


class MonthlyIncomeMapper:
    @staticmethod
    def to_entity(model: MonthlyIncomeModel) -> MonthlyIncome:
        """SQLAlchemy Model → Domain Entity"""
        return MonthlyIncome(
            id=model.id,
            user_id= model.user_id,
            period=Period.from_string(f"{model.period_year}{model.period_month:02d}"),
            amount=Money(Decimal(f"{model.amount_value}"), Currency(model.amount_currency)),
            source=IncomeSource(model.source)
        )

    @staticmethod
    def to_model(entity: MonthlyIncome) -> MonthlyIncomeModel:
        """Domain Entity → SQLAlchemy Model"""
        return MonthlyIncomeModel(
            id=entity.id,
            user_id=entity.user_id,
            period_year=entity.period.year,
            period_month=entity.period.month,
            amount_value=float(entity.amount.amount),
            amount_currency=entity.amount.currency,
            source=entity.source
        )
