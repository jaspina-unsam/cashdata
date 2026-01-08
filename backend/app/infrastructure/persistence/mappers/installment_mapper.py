from decimal import Decimal

from app.domain.entities.installment import Installment
from app.domain.value_objects.money import Money, Currency
from app.infrastructure.persistence.models.installment_model import InstallmentModel


class InstallmentMapper:
    @staticmethod
    def to_entity(model: InstallmentModel) -> Installment:
        """SQLAlchemy Model → Domain Entity"""
        return Installment(
            id=model.id,
            purchase_id=model.purchase_id,
            installment_number=model.installment_number,
            total_installments=model.total_installments,
            amount=Money(Decimal(str(model.amount)), Currency(model.currency)),
            billing_period=model.billing_period,
        )

    @staticmethod
    def to_model(entity: Installment) -> InstallmentModel:
        """Domain Entity → SQLAlchemy Model"""
        return InstallmentModel(
            id=entity.id,
            purchase_id=entity.purchase_id,
            installment_number=entity.installment_number,
            total_installments=entity.total_installments,
            amount=float(entity.amount.amount),
            currency=entity.amount.currency.value,
            billing_period=entity.billing_period,
        )
