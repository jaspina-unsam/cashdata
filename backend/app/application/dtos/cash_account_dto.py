from app.domain.value_objects.money import Currency
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateCashAccountInputDTO(BaseModel):
    user_id: int = Field(gt=0, description="User ID")
    name: str = Field(
        min_length=1, max_length=100, description="Name of the cash account"
    )
    currency: Currency = Field(default=Currency.ARS, description="Currency of the cash account")

    @field_validator("name")
    @classmethod
    def name_must_not_be_only_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be only whitespace")
        return v.strip()

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "user_id": 1,
                "name": "My Cash Wallet",
                "currency": "USD",
            }
        },
    )


class CashAccountResponseDTO(BaseModel):
    """Response DTO for CashAccount"""

    id: int
    payment_method_id: int
    user_id: int
    name: str
    currency: Currency

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "payment_method_id": 1,
                "user_id": 1,
                "name": "My Cash Wallet",
                "currency": "USD",
            }
        },
    )