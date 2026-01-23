from decimal import Decimal

from app.domain.entities.exchange_rate import ExchangeRate
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.value_objects.money import Currency
from app.infrastructure.persistence.models.exchange_rate_model import ExchangeRateModel


class ExchangeRateMapper:
    @staticmethod
    def to_entity(model: ExchangeRateModel) -> ExchangeRate:
        """SQLAlchemy Model → Domain Entity"""
        return ExchangeRate(
            id=model.id,
            date=model.date,
            from_currency=Currency(model.from_currency),
            to_currency=Currency(model.to_currency),
            rate=Decimal(str(model.rate)),
            rate_type=ExchangeRateType(model.rate_type),
            source=model.source,
            notes=model.notes,
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: ExchangeRate) -> ExchangeRateModel:
        """Domain Entity → SQLAlchemy Model"""
        return ExchangeRateModel(
            id=entity.id,
            date=entity.date,
            from_currency=entity.from_currency.value,
            to_currency=entity.to_currency.value,
            rate=float(entity.rate),
            rate_type=entity.rate_type.value,
            source=entity.source,
            notes=entity.notes,
            created_by_user_id=entity.created_by_user_id,
            created_at=entity.created_at,
        )
