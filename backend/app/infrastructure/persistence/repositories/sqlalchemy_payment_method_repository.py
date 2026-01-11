from typing import List, Optional
from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.infrastructure.persistence.mappers.payment_method_mapper import (
    PaymentMethodMapper,
)
from app.infrastructure.persistence.models.payment_method_model import (
    PaymentMethodModel,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.repositories.ipayment_method_repository import IPaymentMethodRepository


class SQLAlchemyPaymentMethodRepository(IPaymentMethodRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, payment_method_id: int) -> Optional[PaymentMethod]:
        paymethod = self.session.scalars(
            select(PaymentMethodModel).where(PaymentMethodModel.id == payment_method_id)
        ).first()
        return PaymentMethodMapper.to_entity(paymethod) if paymethod else None

    def find_by_user_id(
        self, user_id: int, type: Optional[PaymentMethodType] = None
    ) -> List[PaymentMethod]:
        paymethods = self.session.scalars(
            select(PaymentMethodModel).where(
                PaymentMethodModel.user_id == user_id,
                PaymentMethodModel.type == type if type is not None else True,
            )
        ).all()
        return [PaymentMethodMapper.to_entity(pm) for pm in paymethods]

    def save(self, payment_method: PaymentMethod) -> PaymentMethod:
        if payment_method.id is not None:
            # Update existing
            existing = self.session.get(PaymentMethodModel, payment_method.id)
            if existing:
                existing.user_id = payment_method.user_id
                existing.type = payment_method.type
                existing.name = payment_method.name
                existing.is_active = payment_method.is_active
                existing.updated_at = payment_method.updated_at
                self.session.flush()
                self.session.refresh(existing)
                return PaymentMethodMapper.to_entity(existing)

        # Insert new
        model = PaymentMethodMapper.to_model(payment_method)
        model.id = None  # Ensure new ID is generated
        merged_model = self.session.merge(model)
        self.session.flush()
        self.session.refresh(merged_model)
        return PaymentMethodMapper.to_entity(merged_model)

    def delete(self, payment_method_id: int) -> None:
        paymethod = self.session.get(PaymentMethodModel, payment_method_id)
        if paymethod:
            self.session.delete(paymethod)
            self.session.flush()
