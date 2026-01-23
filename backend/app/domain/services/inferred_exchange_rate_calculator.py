from datetime import date, datetime, timezone
from decimal import Decimal
from app.domain.entities.exchange_rate import ExchangeRate
from app.domain.exceptions.domain_exceptions import InvalidCalculation
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.value_objects.money import Currency


class InferredExchangeRateCalculator:
    """Calculates inferred exchange rates between two currencies based on dual-currency purchases."""

    def calculate_inferred_rate(
        self,
        original_amount: Decimal,
        original_currency: Currency,
        converted_amount: Decimal,
        converted_currency: Currency,
    ) -> Decimal:
        if original_currency == Currency.USD and converted_currency == Currency.ARS:
            return converted_amount / original_amount
        elif original_currency == Currency.ARS and converted_currency == Currency.USD:
            return original_amount / converted_amount
        else:
            raise InvalidCalculation("Invalid currency pair for inference.")

    def create_inferred_rate_entity(
        self,
        purchase_date: date,
        original_amount: Decimal,
        original_currency: Currency,
        converted_amount: Decimal,
        converted_currency: Currency,
        user_id: int,
    ) -> ExchangeRate:
        rate = self.calculate_inferred_rate(
            original_amount,
            original_currency,
            converted_amount,
            converted_currency,
        )

        return ExchangeRate(
            id=None,
            date=purchase_date,
            from_currency=Currency.USD,
            to_currency=Currency.ARS,
            rate=rate,
            rate_type=ExchangeRateType.INFERRED,
            source="calculated",
            notes=f"Inferred from purchase: {original_amount} {original_currency} -> {converted_amount} {converted_currency}",
            created_by_user_id=user_id,
            created_at=datetime.now(timezone.utc),
        )
