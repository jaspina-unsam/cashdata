from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import date, datetime

from app.domain.exceptions.domain_exceptions import InvalidMoneyOperation
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.value_objects.money import Currency


@dataclass(frozen=True)
class ExchangeRate:
    id: Optional[int]
    date: date
    from_currency: Currency
    to_currency: Currency
    rate: Decimal
    rate_type: ExchangeRateType
    created_at: datetime
    source: Optional[str] = None
    notes: Optional[str] = None
    created_by_user_id: Optional[int] = None

    def __post_init__(self):
        if self.rate <= Decimal("0"):
            raise ValueError("Exchange rate must be positive")
        if self.from_currency == self.to_currency:
            raise ValueError("from_currency and to_currency must be different")

    def convert(self, amount: Decimal, from_currency: Currency) -> Decimal:
        if from_currency == self.from_currency:
            return amount * self.rate
        elif from_currency == self.to_currency:
            return amount / self.rate
        else:
            raise InvalidMoneyOperation(
                f"Cannot convert {from_currency} using this exchange rate"
            )
