from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.payment_method_type import PaymentMethodType


class PaymentMethodValidator:
    # Validate that only credit cards can have installments >= 1
    @staticmethod
    def validate_installments(payment_method: PaymentMethod, installments_count: int) -> bool:
        return not (
            installments_count > 1
            and payment_method.type != PaymentMethodType.CREDIT_CARD
        )
