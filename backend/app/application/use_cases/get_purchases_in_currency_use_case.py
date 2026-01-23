from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional

from app.domain.entities.purchase import Purchase
from app.domain.entities.exchange_rate import ExchangeRate
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.services.currency_converter import CurrencyConverter
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.value_objects.money import Currency


@dataclass(frozen=True)
class GetPurchasesInCurrencyQuery:
    """Query to get purchases converted to a specific currency"""

    user_id: int
    target_currency: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    preferred_rate_type: Optional[str] = None


@dataclass(frozen=True)
class PurchaseInCurrency:
    """Purchase with amount in target currency"""

    purchase: Purchase
    amount_in_target_currency: Decimal
    exchange_rate_used: Optional[ExchangeRate]


@dataclass(frozen=True)
class GetPurchasesInCurrencyResult:
    """Result of getting purchases in a specific currency"""

    purchases: List[PurchaseInCurrency]


class GetPurchasesInCurrencyUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(
        self, query: GetPurchasesInCurrencyQuery
    ) -> GetPurchasesInCurrencyResult:
        """
        Get purchases converted to a specific currency

        Args:
            query: The query containing target currency and filters

        Returns:
            GetPurchasesInCurrencyResult: Purchases with converted amounts
        """
        with self.unit_of_work as uow:
            # Load purchases
            all_purchases = uow.purchases.find_by_user_id(query.user_id)

            # Filter by date range if specified
            if query.start_date or query.end_date:
                filtered_purchases = []
                for purchase in all_purchases:
                    if query.start_date and purchase.purchase_date < query.start_date:
                        continue
                    if query.end_date and purchase.purchase_date > query.end_date:
                        continue
                    filtered_purchases.append(purchase)
                all_purchases = filtered_purchases

            target_currency = Currency(query.target_currency)
            preferred_rate_type = (
                ExchangeRateType(query.preferred_rate_type)
                if query.preferred_rate_type
                else None
            )

            # Create currency converter
            converter = CurrencyConverter(uow.exchange_rates)

            # Convert each purchase
            results = []
            for purchase in all_purchases:
                # Try to get amount in target currency
                try:
                    amount_in_target = purchase.get_amount_in_currency(target_currency)
                    # Already in target currency, no conversion needed
                    results.append(
                        PurchaseInCurrency(
                            purchase=purchase,
                            amount_in_target_currency=amount_in_target,
                            exchange_rate_used=None,
                        )
                    )
                except:
                    # Need conversion
                    source_currency = purchase.total_amount.primary_currency
                    converted_amount, exchange_rate = converter.convert(
                        amount=purchase.total_amount.primary_amount,
                        from_currency=source_currency,
                        to_currency=target_currency,
                        reference_date=purchase.purchase_date,
                        preferred_type=preferred_rate_type,
                        user_id=query.user_id,
                    )

                    results.append(
                        PurchaseInCurrency(
                            purchase=purchase,
                            amount_in_target_currency=converted_amount,
                            exchange_rate_used=exchange_rate,
                        )
                    )

            return GetPurchasesInCurrencyResult(purchases=results)
