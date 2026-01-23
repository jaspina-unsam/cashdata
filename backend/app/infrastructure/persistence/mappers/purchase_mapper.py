from decimal import Decimal
from typing import Optional

from app.domain.entities.purchase import Purchase
from app.domain.value_objects.money import Money, Currency
from app.domain.value_objects.dual_money import DualMoney
from app.infrastructure.persistence.models.purchase_model import PurchaseModel


class PurchaseMapper:
    @staticmethod
    def to_entity(model: PurchaseModel) -> Purchase:
        """SQLAlchemy Model → Domain Entity"""
        # Build DualMoney from model fields
        # Only create dual-currency DualMoney if we have all three required fields
        if (model.original_amount is not None and 
            model.original_currency is not None and 
            model.exchange_rate_id is not None and
            model.total_currency != model.original_currency):  # Must be different currencies
            # Dual-currency purchase - calculate exchange rate from amounts
            # Rate is always how much of to_currency you get for 1 unit of from_currency
            if model.total_currency == "ARS" and model.original_currency == "USD":
                # USD to ARS: ARS amount / USD amount
                calculated_rate = Decimal(str(model.total_amount)) / Decimal(str(model.original_amount))
            elif model.total_currency == "USD" and model.original_currency == "ARS":
                # ARS to USD: USD amount / ARS amount (inverse)
                calculated_rate = Decimal(str(model.total_amount)) / Decimal(str(model.original_amount))
            else:
                # Other currency combinations
                calculated_rate = Decimal(str(model.total_amount)) / Decimal(str(model.original_amount))
            
            total_amount = DualMoney(
                primary_amount=Decimal(str(model.total_amount)),
                primary_currency=Currency(model.total_currency),
                secondary_amount=Decimal(str(model.original_amount)),
                secondary_currency=Currency(model.original_currency),
                exchange_rate=calculated_rate
            )
        else:
            # Single-currency purchase (or incomplete dual-currency data)
            total_amount = DualMoney(
                primary_amount=Decimal(str(model.total_amount)),
                primary_currency=Currency(model.total_currency),
            )
        
        return Purchase(
            id=model.id,
            user_id=model.user_id,
            payment_method_id=model.payment_method_id,
            category_id=model.category_id,
            purchase_date=model.purchase_date,
            description=model.description,
            total_amount=total_amount,
            installments_count=model.installments_count,
        )

    @staticmethod
    def to_model(entity: Purchase) -> PurchaseModel:
        """Domain Entity → SQLAlchemy Model"""
        # Extract dual-currency fields if present
        original_currency: Optional[str] = None
        original_amount: Optional[float] = None
        exchange_rate_id: Optional[int] = None
        
        if entity.total_amount.is_dual_currency():
            original_currency = entity.total_amount.secondary_currency.value
            original_amount = float(entity.total_amount.secondary_amount)
            # Note: exchange_rate_id should be set by the use case/service layer
        
        return PurchaseModel(
            id=entity.id,
            user_id=entity.user_id,
            payment_method_id=entity.payment_method_id,
            category_id=entity.category_id,
            purchase_date=entity.purchase_date,
            description=entity.description,
            total_amount=float(entity.total_amount.primary_amount),
            total_currency=entity.total_amount.primary_currency.value,
            installments_count=entity.installments_count,
            original_currency=original_currency,
            original_amount=original_amount,
            exchange_rate_id=exchange_rate_id,
        )
