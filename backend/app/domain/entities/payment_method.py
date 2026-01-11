from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.exceptions.domain_exceptions import PaymentMethodNameError
from app.domain.value_objects.payment_method_type import PaymentMethodType


@dataclass(frozen=True)
class PaymentMethod:
    """
    Parent domain entity for Credit Card, Cash, Bank Account and Digital Wallet.
    """

    id: Optional[int]
    user_id: int
    type: PaymentMethodType
    name: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise PaymentMethodNameError("Payment method name cannot be empty")

    def __eq__(self, other) -> bool:
        if not isinstance(other, PaymentMethod):
            return False
        if self.id is None and other.id is None:
            return self is other
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id) if self.id is not None else id(self)
