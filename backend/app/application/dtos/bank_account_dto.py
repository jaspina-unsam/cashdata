from typing import Optional
from app.domain.value_objects.money import Currency
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateBankAccountInputDTO(BaseModel):
    """
    Input DTO for creating a bank account.
    
    Bank accounts can have one or two owners:
    - primary_user_id: The primary owner/titular (required)
    - secondary_user_id: Optional second owner for joint accounts (e.g., spouses)
    
    This explicit specification allows for scenarios where someone manages
    finances for another person or creates joint accounts.
    
    Note: In production with authentication, ensure proper authorization
    checks to verify the requesting user has permission to create accounts
    for the specified user_id(s).
    """
    primary_user_id: int = Field(
        gt=0, 
        description="ID of the primary owner/titular of the bank account"
    )
    secondary_user_id: int | None = Field(
        gt=0, 
        description="Optional ID of the secondary owner for joint accounts", 
        default=None
    )
    name: str = Field(
        min_length=1, 
        max_length=100, 
        description="Descriptive name for the account (e.g., 'Cuenta Familiar Santander')"
    )
    bank: str = Field(
        min_length=1, 
        max_length=100, 
        description="Name of the bank (e.g., 'Santander', 'Galicia')"
    )
    account_type: str = Field(
        min_length=1, 
        max_length=50, 
        description="Type of account (e.g., 'savings', 'checking')"
    )
    last_four_digits: str = Field(
        min_length=4, 
        max_length=4, 
        description="Last 4 digits of the account number"
    )
    currency: Currency = Field(
        default=Currency.ARS, 
        description="Currency of the account"
    )

    @field_validator("name", "bank", "account_type", "last_four_digits")
    @classmethod
    def fields_must_not_be_only_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be only whitespace")
        return v.strip()

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "primary_user_id": 1,
                "secondary_user_id": 2,
                "name": "My Bank Account",
                "bank": "Bank of Examples",
                "account_type": "Checking",
                "last_four_digits": "1234",
                "currency": "USD",
            }
        },
    )

class BankAccountResponseDTO(BaseModel):
    """Response DTO for BankAccount"""

    id: int
    payment_method_id: int
    primary_user_id: int
    secondary_user_id: Optional[int]
    name: str
    bank: str
    account_type: str
    last_four_digits: str
    currency: Currency

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "payment_method_id": 1,
                "primary_user_id": 1,
                "secondary_user_id": 2,
                "name": "My Bank Account",
                "bank": "Bank of Examples",
                "account_type": "Checking",
                "last_four_digits": "1234",
                "currency": "USD",
            }
        },
    )