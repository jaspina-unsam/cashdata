from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.infrastructure.persistence.models.payment_method_model import (
    PaymentMethodModel,
)


class PaymentMethodMapper:
    @staticmethod
    def to_entity(model: PaymentMethodModel) -> PaymentMethod:
        return PaymentMethod(
            id=model.id,
            user_id=model.user_id,
            type=PaymentMethodType(model.type),
            name=model.name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: PaymentMethod) -> PaymentMethodModel:
        return PaymentMethodModel(
            id=entity.id,
            user_id=entity.user_id,
            type=entity.type.value,
            name=entity.name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
