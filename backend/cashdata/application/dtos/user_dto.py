from uuid import UUID
from decimal import Decimal
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    field_validator,
    ConfigDict,
)
from cashdata.domain.value_objects.money import Currency


class CreateUserInputDTO(BaseModel):
    """Input DTO for user creation with format validations"""

    name: str = Field(min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(description="User's email address")
    wage_amount: Decimal = Field(
        gt=0, description="Monthly wage amount (must be positive)"
    )
    wage_currency: Currency = Field(default=Currency.ARS, description="Wage currency")

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
                "name": "John Locke",
                "email": "juan@example.com",
                "wage_amount": "50000.00",
                "wage_currency": "ARS",
            }
        },
    )


class UserResponseDTO(BaseModel):
    """Response DTO for User - flattened for API consumption"""

    id: int
    name: str
    email: str
    wage_amount: Decimal
    wage_currency: Currency

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Juan Pérez",
                "email": "juan@example.com",
                "wage_amount": "50000.00",
                "wage_currency": "ARS",
            }
        },
    )
