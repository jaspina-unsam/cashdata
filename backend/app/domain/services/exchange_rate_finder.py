from datetime import date
from typing import Optional

from app.domain.entities.exchange_rate import ExchangeRate
from app.domain.repositories.iexchange_rate_repository import IExchangeRateRepository
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.value_objects.money import Currency


class ExchangeRateFinder:
    """Finds the most appropriate exchange rate according to a given date and type."""

    def __init__(self, exchange_rate_repository: IExchangeRateRepository):
        self.repo = exchange_rate_repository

    def find_exchange_rate(
        self,
        date: date,
        from_currency: Currency,
        to_currency: Currency,
        preferred_type: Optional[ExchangeRateType] = None,
        user_id: Optional[int] = None,
    ) -> Optional[ExchangeRate]:
        """Find the most recent exchange rate on or before the given date."""
        # Try by exact date first
        if preferred_type:
            rate = self.repo.get_by_date_and_type(
                date, from_currency, to_currency, preferred_type, user_id
            )
            if rate:
                return rate

        # Try close date with preferred type
        if preferred_type:
            rate = self.repo.find_closest_by_date_and_type(
                date, from_currency, to_currency, preferred_type, user_id
            )
            if rate:
                return rate

        # Priority search
        priority_order = [
            ExchangeRateType.CUSTOM,
            ExchangeRateType.OFFICIAL,
            ExchangeRateType.BLUE,
            ExchangeRateType.INFERRED,
        ]

        for rate_type in priority_order:
            rate = self.repo.find_by_date_and_type(
                date, from_currency, to_currency, rate_type, user_id
            )
            if rate:
                return rate

        # Fallback to any type
        return self.repo.find_closest(date, from_currency, to_currency, user_id)
