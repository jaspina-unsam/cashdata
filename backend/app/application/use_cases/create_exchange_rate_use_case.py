from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from app.domain.entities.exchange_rate import ExchangeRate
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.value_objects.money import Currency


@dataclass(frozen=True)
class CreateExchangeRateCommand:
    """Command to create a new exchange rate"""

    date: date
    from_currency: str
    to_currency: str
    rate: Decimal
    rate_type: str
    user_id: int
    source: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class CreateExchangeRateResult:
    """Result of creating an exchange rate"""

    exchange_rate_id: int


class CreateExchangeRateUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, command: CreateExchangeRateCommand) -> CreateExchangeRateResult:
        """
        Create a new exchange rate

        Args:
            command: The command containing exchange rate details

        Returns:
            CreateExchangeRateResult: The result containing exchange rate ID

        Raises:
            ValueError: If rate is invalid or duplicate exists
        """
        with self.unit_of_work as uow:
            # Validate rate is positive
            if command.rate <= Decimal("0"):
                raise ValueError("Exchange rate must be positive")

            # Parse currencies and rate_type
            from_currency = Currency(command.from_currency)
            to_currency = Currency(command.to_currency)
            rate_type = ExchangeRateType(command.rate_type)

            # Check for existing rate with same date, currencies, and type
            existing_rate = uow.exchange_rates.get_by_date_and_type(
                date=command.date,
                from_currency=from_currency,
                to_currency=to_currency,
                rate_type=rate_type,
                user_id=command.user_id if rate_type == ExchangeRateType.CUSTOM else None,
            )

            if existing_rate:
                raise ValueError(
                    f"Exchange rate already exists for {command.date} "
                    f"({from_currency.value} → {to_currency.value}, {rate_type.value})"
                )

            # Create exchange rate entity
            exchange_rate = ExchangeRate(
                id=None,
                date=command.date,
                from_currency=from_currency,
                to_currency=to_currency,
                rate=command.rate,
                rate_type=rate_type,
                source=command.source,
                notes=command.notes,
                created_by_user_id=command.user_id,
                created_at=datetime.now(),
            )

            # Save exchange rate
            saved_rate = uow.exchange_rates.save(exchange_rate)

            # Commit transaction
            uow.commit()

            return CreateExchangeRateResult(exchange_rate_id=saved_rate.id)
