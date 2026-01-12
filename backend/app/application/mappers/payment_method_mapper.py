from app.domain.entities.payment_method import PaymentMethod
from app.application.dtos.payment_method_dto import PaymentMethodResponseDTO


class PaymentMethodDTOMapper:
    """Maps between PaymentMethod entity and DTOs"""

    @staticmethod
    def to_response_dto(payment_method: PaymentMethod) -> PaymentMethodResponseDTO:
        """Convert domain entity to response DTO"""
        return PaymentMethodResponseDTO(
            id=payment_method.id,
            user_id=payment_method.user_id,
            type=payment_method.type,
            name=payment_method.name,
            is_active=payment_method.is_active,
            created_at=payment_method.created_at,
            updated_at=payment_method.updated_at,
        )