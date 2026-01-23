from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.domain.exceptions.domain_exceptions import InvalidMoneyOperation
from app.domain.value_objects.money import Currency


@dataclass(frozen=True)
class DualMoney:
    primary_amount: Decimal
    primary_currency: Currency
    secondary_amount: Optional[Decimal] = None
    secondary_currency: Optional[Currency] = None
    exchange_rate: Optional[Decimal] = None

    def __post_init__(self):
        if self.secondary_amount is not None:
            if self.secondary_currency is None:
                raise InvalidMoneyOperation(
                    "secondary_currency required with secondary_amount"
                )
            if self.exchange_rate is None:
                raise InvalidMoneyOperation("exchange_rate is required")

    def is_dual_currency(self) -> bool:
        return self.secondary_amount is not None

    def in_currency(self, currency: Currency) -> Decimal:
        if self.primary_currency == currency:
            return self.primary_amount
        if self.secondary_currency == currency:
            return self.secondary_amount
        else:
            raise InvalidMoneyOperation(f"Amount not available in {currency}")

    # Compatibility properties for Money interface
    @property
    def amount(self) -> Decimal:
        """Alias for primary_amount to maintain backward compatibility with Money"""
        return self.primary_amount

    @property
    def currency(self) -> Currency:
        """Alias for primary_currency to maintain backward compatibility with Money"""
        return self.primary_currency

    def __eq__(self, other) -> bool:
        """
        Check equality with Money or DualMoney.
        
        When comparing with Money, only compares if this is single-currency.
        """
        if isinstance(other, DualMoney):
            return (
                self.primary_amount == other.primary_amount
                and self.primary_currency == other.primary_currency
                and self.secondary_amount == other.secondary_amount
                and self.secondary_currency == other.secondary_currency
                and self.exchange_rate == other.exchange_rate
            )
        
        # Allow comparison with Money when single-currency
        from app.domain.value_objects.money import Money
        if isinstance(other, Money):
            if self.is_dual_currency():
                return False
            return (
                self.primary_amount == other.amount
                and self.primary_currency == other.currency
            )
        
        return False
