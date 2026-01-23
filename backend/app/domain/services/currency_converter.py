from typing import Optional
from datetime import date
from decimal import Decimal
from app.domain.entities.exchange_rate import ExchangeRate
from app.domain.exceptions.domain_exceptions import ExchangeRateNotFound
from app.domain.services.exchange_rate_finder import ExchangeRateFinder
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.value_objects.money import Currency, Money


class CurrencyConverter:
    """Converts amounts between different currencies using exchange rates."""

    def __init__(
        self,
        exchange_rate_finder: ExchangeRateFinder,
    ):
        self.rate_finder = exchange_rate_finder

    def convert(
        self,
        amount: Decimal,
        from_currency: Currency,
        to_currency: Currency,
        reference_date: date,
        preffered_rate_type: Optional[ExchangeRateType] = None,
        user_id: Optional[int] = None,
    ) -> tuple[Decimal, Optional[ExchangeRate]]:
        if from_currency == to_currency:
            return (amount, None)

        rate = self.rate_finder.find_best_rate(
            reference_date,
            from_currency if from_currency == Currency.USD else to_currency,
            to_currency if from_currency == Currency.USD else from_currency,
            preffered_rate_type,
            user_id,
        )

        if not rate:
            raise ExchangeRateNotFound(
                f"No exchange rate found for {from_currency} to {to_currency} on {reference_date}"
            )

        converted = rate.convert(amount, from_currency)
        return (converted, rate)

    def convert_money(
        self,
        money: Money,
        to_currency: Currency,
        reference_date: date,
        preferred_rate_type: Optional[ExchangeRateType] = None,
        user_id: Optional[int] = None,
    ) -> tuple[Money, Optional[ExchangeRate]]:
        converted_amount, rate = self.convert(
            money.amount,
            money.currency,
            to_currency,
            reference_date,
            preferred_rate_type,
            user_id,
        )
        return (Money(converted_amount, to_currency), rate)
