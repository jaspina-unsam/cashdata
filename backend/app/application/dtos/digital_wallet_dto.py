from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.domain.value_objects.money import Currency


class CreateDigitalWalletInputDTO(BaseModel):
    """
    Input DTO for creating a digital wallet.
    
    The user_id field specifies the owner/titular of the digital wallet.
    This explicit specification allows for scenarios where someone manages
    finances for another person (e.g., parents for children, accountants
    for clients, or financial tutors).
    
    Note: In production with authentication, ensure proper authorization
    checks to verify the requesting user has permission to create wallets
    for the specified user_id.
    """
    user_id: int = Field(
        gt=0,
        description="ID of the user who will own this digital wallet (titular)"
    )
    name: str = Field(
        min_length=1, 
        max_length=100,
        description="Descriptive name for the wallet (e.g., 'MercadoPago - Juan')"
    )
    provider: str = Field(
        min_length=1, 
        max_length=100,
        description="Wallet provider (mercadopago, personalpay, other)"
    )
    identifier: str | None = Field(
        default=None,
        description="Optional identifier (phone, email, or account ID)"
    )
    currency: Currency = Field(
        default=Currency.ARS,
        description="Primary currency of the wallet"
    )

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
