from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.domain.value_objects.money import Currency


class CreateDigitalWalletInputDTO(BaseModel):
    user_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100)
    provider: str = Field(min_length=1, max_length=100)
    identifier: str | None = None
    currency: Currency = Field(default=Currency.ARS)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be only whitespace")
        return v.strip()

    model_config = ConfigDict(use_enum_values=True)


class DigitalWalletResponseDTO(BaseModel):
    id: int
    payment_method_id: int
    user_id: int
    name: str
    provider: str
    identifier: str | None
    currency: Currency

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
