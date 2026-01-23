from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List

from app.domain.entities.exchange_rate import ExchangeRate
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.value_objects.money import Currency


class IExchangeRateRepository(ABC):
    @abstractmethod
    def find_by_id(self, rate_id: int) -> Optional[ExchangeRate]:
        """Find exchange rate by its ID."""
        pass

    @abstractmethod
    def get_by_date_and_type(
        self,
        date: date,
        from_currency: Currency,
        to_currency: Currency,
        rate_type: ExchangeRateType,
        user_id: Optional[int] = None,
    ) -> Optional[ExchangeRate]:
        """Retrieve exchange rate by exact date and type."""
        pass

    @abstractmethod
    def find_closest_by_date_and_type(
        self,
        date: date,
        from_currency: Currency,
        to_currency: Currency,
        rate_type: ExchangeRateType,
        user_id: Optional[int] = None,
    ) -> Optional[ExchangeRate]:
        """Find the closest exchange rate on or before the given date with specified type."""
        pass

    @abstractmethod
    def find_by_date_and_type(
        self,
        date: date,
        from_currency: Currency,
        to_currency: Currency,
        rate_type: ExchangeRateType,
        user_id: Optional[int] = None,
    ) -> Optional[ExchangeRate]:
        """Find exchange rate on or before the given date with specified type."""
        pass

    @abstractmethod
    def find_closest(
        self,
        reference_date: date,
        from_currency: Currency,
        to_currency: Currency,
        user_id: Optional[int] = None,
        max_days_diff: Optional[int] = 30,
    ) -> Optional[ExchangeRate]:
        """Find the closest exchange rate on or before the given date, regardless of type."""
        pass

    @abstractmethod
    def save(self, rate: ExchangeRate) -> ExchangeRate:
        """Save or update an exchange rate entity."""
        pass

    @abstractmethod
    def delete(self, rate_id: int) -> None:
        """Delete an exchange rate by its ID."""
        pass

    @abstractmethod
    def list_all(
        self,
        from_currency: Optional[Currency] = None,
        to_currency: Optional[Currency] = None,
        rate_type: Optional[ExchangeRateType] = None,
        user_id: Optional[int] = None,
    ) -> List[ExchangeRate]:
        """List all exchange rates, optionally filtered by currency, type, or user."""
        pass