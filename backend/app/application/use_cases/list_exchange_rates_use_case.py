from dataclasses import dataclass
from datetime import date
from typing import Optional, List

from app.domain.entities.exchange_rate import ExchangeRate
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.value_objects.money import Currency


@dataclass(frozen=True)
class ListExchangeRatesQuery:
    """Query to list exchange rates within a date range"""

    start_date: date
    end_date: date
    from_currency: Optional[str] = None
    to_currency: Optional[str] = None
    rate_type: Optional[str] = None
    user_id: Optional[int] = None


@dataclass(frozen=True)
class ListExchangeRatesResult:
    """Result of listing exchange rates"""

    exchange_rates: List[ExchangeRate]


class ListExchangeRatesByDateRangeUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: ListExchangeRatesQuery) -> ListExchangeRatesResult:
        """
        List exchange rates within a date range

        Args:
            query: The query containing filter criteria

        Returns:
            ListExchangeRatesResult: The result containing list of exchange rates
        """
        with self.unit_of_work as uow:
            # Get all exchange rates (we'll filter by date in Python)
            from_currency = Currency(query.from_currency) if query.from_currency else None
            to_currency = Currency(query.to_currency) if query.to_currency else None
            rate_type = ExchangeRateType(query.rate_type) if query.rate_type else None

            all_rates = uow.exchange_rates.list_all(
                from_currency=from_currency,
                to_currency=to_currency,
                rate_type=rate_type,
                user_id=query.user_id,
            )

            # Filter by date range
            filtered_rates = [
                rate
                for rate in all_rates
                if query.start_date <= rate.date <= query.end_date
            ]

            return ListExchangeRatesResult(exchange_rates=filtered_rates)
