from decimal import Decimal

from app.domain.entities.purchase import Purchase
from app.domain.value_objects.money import Money, Currency
from app.infrastructure.persistence.models.purchase_model import PurchaseModel


class PurchaseMapper:
    @staticmethod
    def to_entity(model: PurchaseModel) -> Purchase:
        """SQLAlchemy Model → Domain Entity"""
        return Purchase(
            id=model.id,
            user_id=model.user_id,
            credit_card_id=model.credit_card_id,
            category_id=model.category_id,
            purchase_date=model.purchase_date,
            description=model.description,
            total_amount=Money(
                Decimal(str(model.total_amount)), Currency(model.total_currency)
            ),
            installments_count=model.installments_count,
        )

    @staticmethod
    def to_model(entity: Purchase) -> PurchaseModel:
        """Domain Entity → SQLAlchemy Model"""
        return PurchaseModel(
            id=entity.id,
            user_id=entity.user_id,
            credit_card_id=entity.credit_card_id,
            category_id=entity.category_id,
            purchase_date=entity.purchase_date,
            description=entity.description,
            total_amount=float(entity.total_amount.amount),
            total_currency=entity.total_amount.currency.value,
            installments_count=entity.installments_count,
        )
