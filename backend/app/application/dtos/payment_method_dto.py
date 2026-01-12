from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.domain.value_objects.payment_method_type import PaymentMethodType


class PaymentMethodResponseDTO(BaseModel):
    """Response DTO for PaymentMethod"""

    id: int
    user_id: int
    type: PaymentMethodType
    name: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "type": "credit_card",
                "name": "Visa Gold",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": None,
            }
        },
    )