from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.domain.entities.exchange_rate import ExchangeRate
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.value_objects.money import Currency


@dataclass(frozen=True)
class GetLatestExchangeRateQuery:
    """Query to get the latest exchange rate"""

    from_currency: str
    to_currency: str
    rate_type: str
    user_id: Optional[int] = None
    reference_date: Optional[date] = None


@dataclass(frozen=True)
class GetLatestExchangeRateResult:
    """Result of getting latest exchange rate"""

    exchange_rate: Optional[ExchangeRate]


class GetLatestExchangeRateUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: GetLatestExchangeRateQuery) -> GetLatestExchangeRateResult:
        """
        Get the latest exchange rate for a given type

        Args:
            query: The query containing rate type and currencies

        Returns:
            GetLatestExchangeRateResult: The result containing the latest exchange rate
        """
        with self.unit_of_work as uow:
            from_currency = Currency(query.from_currency)
            to_currency = Currency(query.to_currency)
            rate_type = ExchangeRateType(query.rate_type)

            # Use reference_date or today
            ref_date = query.reference_date or date.today()

            # Find closest rate on or before reference date
            exchange_rate = uow.exchange_rates.find_closest_by_date_and_type(
                date=ref_date,
                from_currency=from_currency,
                to_currency=to_currency,
                rate_type=rate_type,
                user_id=query.user_id if rate_type == ExchangeRateType.CUSTOM else None,
            )

            return GetLatestExchangeRateResult(exchange_rate=exchange_rate)
