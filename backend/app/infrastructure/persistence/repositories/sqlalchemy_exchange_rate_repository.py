from datetime import date, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from app.domain.entities.exchange_rate import ExchangeRate
from app.domain.repositories.iexchange_rate_repository import IExchangeRateRepository
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.value_objects.money import Currency
from app.infrastructure.persistence.mappers.exchange_rate_mapper import ExchangeRateMapper
from app.infrastructure.persistence.models.exchange_rate_model import ExchangeRateModel


class SQLAlchemyExchangeRateRepository(IExchangeRateRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, rate_id: int) -> Optional[ExchangeRate]:
        """Find exchange rate by its ID."""
        model = self.session.scalars(
            select(ExchangeRateModel).where(ExchangeRateModel.id == rate_id)
        ).first()
        return ExchangeRateMapper.to_entity(model) if model else None

    def get_by_date_and_type(
        self,
        date: date,
        from_currency: Currency,
        to_currency: Currency,
        rate_type: ExchangeRateType,
        user_id: Optional[int] = None,
    ) -> Optional[ExchangeRate]:
        """Retrieve exchange rate by exact date and type."""
        query = select(ExchangeRateModel).where(
            and_(
                ExchangeRateModel.date == date,
                ExchangeRateModel.from_currency == from_currency.value,
                ExchangeRateModel.to_currency == to_currency.value,
                ExchangeRateModel.rate_type == rate_type.value,
            )
        )
        
        if user_id is not None and rate_type == ExchangeRateType.CUSTOM:
            query = query.where(ExchangeRateModel.created_by_user_id == user_id)
        
        model = self.session.scalars(query).first()
        return ExchangeRateMapper.to_entity(model) if model else None

    def find_closest_by_date_and_type(
        self,
        date: date,
        from_currency: Currency,
        to_currency: Currency,
        rate_type: ExchangeRateType,
        user_id: Optional[int] = None,
    ) -> Optional[ExchangeRate]:
        """Find the closest exchange rate on or before the given date with specified type."""
        query = select(ExchangeRateModel).where(
            and_(
                ExchangeRateModel.date <= date,
                ExchangeRateModel.from_currency == from_currency.value,
                ExchangeRateModel.to_currency == to_currency.value,
                ExchangeRateModel.rate_type == rate_type.value,
            )
        ).order_by(ExchangeRateModel.date.desc())
        
        if user_id is not None and rate_type == ExchangeRateType.CUSTOM:
            query = query.where(ExchangeRateModel.created_by_user_id == user_id)
        
        model = self.session.scalars(query).first()
        return ExchangeRateMapper.to_entity(model) if model else None

    def find_by_date_and_type(
        self,
        date: date,
        from_currency: Currency,
        to_currency: Currency,
        rate_type: ExchangeRateType,
        user_id: Optional[int] = None,
    ) -> Optional[ExchangeRate]:
        """Find exchange rate on or before the given date with specified type."""
        return self.find_closest_by_date_and_type(
            date, from_currency, to_currency, rate_type, user_id
        )

    def find_closest(
        self,
        reference_date: date,
        from_currency: Currency,
        to_currency: Currency,
        user_id: Optional[int] = None,
        max_days_diff: Optional[int] = 30,
    ) -> Optional[ExchangeRate]:
        """Find the closest exchange rate on or before the given date, regardless of type."""
        min_date = reference_date - timedelta(days=max_days_diff) if max_days_diff else None
        
        query = select(ExchangeRateModel).where(
            and_(
                ExchangeRateModel.date <= reference_date,
                ExchangeRateModel.from_currency == from_currency.value,
                ExchangeRateModel.to_currency == to_currency.value,
            )
        )
        
        if min_date:
            query = query.where(ExchangeRateModel.date >= min_date)
        
        query = query.order_by(ExchangeRateModel.date.desc())
        
        model = self.session.scalars(query).first()
        return ExchangeRateMapper.to_entity(model) if model else None

    def save(self, rate: ExchangeRate) -> ExchangeRate:
        """Save or update an exchange rate entity."""
        if rate.id is not None:
            # Update existing
            existing = self.session.get(ExchangeRateModel, rate.id)
            if existing:
                existing.date = rate.date
                existing.from_currency = rate.from_currency.value
                existing.to_currency = rate.to_currency.value
                existing.rate = float(rate.rate)
                existing.rate_type = rate.rate_type.value
                existing.source = rate.source
                existing.notes = rate.notes
                existing.created_by_user_id = rate.created_by_user_id
                self.session.flush()
                self.session.refresh(existing)
                return ExchangeRateMapper.to_entity(existing)

        # Insert new
        model = ExchangeRateMapper.to_model(rate)
        merged_model = self.session.merge(model)
        self.session.flush()
        self.session.refresh(merged_model)
        return ExchangeRateMapper.to_entity(merged_model)

    def delete(self, rate_id: int) -> None:
        """Delete an exchange rate by its ID."""
        model = self.session.get(ExchangeRateModel, rate_id)
        if model:
            self.session.delete(model)

    def list_all(
        self,
        from_currency: Optional[Currency] = None,
        to_currency: Optional[Currency] = None,
        rate_type: Optional[ExchangeRateType] = None,
        user_id: Optional[int] = None,
    ) -> List[ExchangeRate]:
        """List all exchange rates, optionally filtered by currency, type, or user."""
        query = select(ExchangeRateModel)
        
        conditions = []
        if from_currency:
            conditions.append(ExchangeRateModel.from_currency == from_currency.value)
        if to_currency:
            conditions.append(ExchangeRateModel.to_currency == to_currency.value)
        if rate_type:
            conditions.append(ExchangeRateModel.rate_type == rate_type.value)
        if user_id is not None:
            conditions.append(ExchangeRateModel.created_by_user_id == user_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ExchangeRateModel.date.desc())
        
        models = self.session.scalars(query).all()
        return [ExchangeRateMapper.to_entity(model) for model in models]
