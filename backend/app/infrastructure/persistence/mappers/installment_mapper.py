from decimal import Decimal
from typing import Optional

from app.domain.entities.installment import Installment
from app.domain.value_objects.money import Money, Currency
from app.domain.value_objects.dual_money import DualMoney
from app.infrastructure.persistence.models.installment_model import InstallmentModel


class InstallmentMapper:
    @staticmethod
    def to_entity(model: InstallmentModel) -> Installment:
        """SQLAlchemy Model → Domain Entity"""
        # Build DualMoney from model fields
        if model.original_amount is not None and model.original_currency is not None:
            # Dual-currency installment
            amount = DualMoney(
                primary_amount=Decimal(str(model.amount)),
                primary_currency=Currency(model.currency),
                secondary_amount=Decimal(str(model.original_amount)),
                secondary_currency=Currency(model.original_currency),
                exchange_rate=None  # Will be computed from exchange_rate_id if needed
            )
        else:
            # Single-currency installment
            amount = DualMoney(
                primary_amount=Decimal(str(model.amount)),
                primary_currency=Currency(model.currency),
            )
        
        return Installment(
            id=model.id,
            purchase_id=model.purchase_id,
            installment_number=model.installment_number,
            total_installments=model.total_installments,
            amount=amount,
            billing_period=model.billing_period,
            manually_assigned_statement_id=model.manually_assigned_statement_id,
        )

    @staticmethod
    def to_model(entity: Installment) -> InstallmentModel:
        """Domain Entity → SQLAlchemy Model"""
        # Extract dual-currency fields if present
        original_currency: Optional[str] = None
        original_amount: Optional[float] = None
        exchange_rate_id: Optional[int] = None
        
        if entity.amount.is_dual_currency():
            original_currency = entity.amount.secondary_currency.value
            original_amount = float(entity.amount.secondary_amount)
            # Note: exchange_rate_id should be set by the use case/service layer
        
        return InstallmentModel(
            id=entity.id,
            purchase_id=entity.purchase_id,
            installment_number=entity.installment_number,
            total_installments=entity.total_installments,
            amount=float(entity.amount.primary_amount),
            currency=entity.amount.primary_currency.value,
            billing_period=entity.billing_period,
            manually_assigned_statement_id=entity.manually_assigned_statement_id,
            original_currency=original_currency,
            original_amount=original_amount,
            exchange_rate_id=exchange_rate_id,
        )
