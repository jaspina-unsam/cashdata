from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.domain.value_objects.money import Currency


class CreatePurchaseInputDTO(BaseModel):
    """Input DTO for purchase creation"""

    credit_card_id: int = Field(gt=0, description="Credit card ID")
    category_id: int = Field(gt=0, description="Category ID")
    purchase_date: date = Field(description="Date of purchase")
    description: str = Field(
        min_length=1, max_length=500, description="Purchase description"
    )
    total_amount: Decimal = Field(
        description="Total purchase amount (positive for purchases, negative for credits)"
    )
    currency: Currency = Field(default=Currency.ARS, description="Currency")
    installments_count: int = Field(
        ge=1, description="Number of installments (minimum 1)"
    )

    @field_validator("description")
    @classmethod
    def description_must_not_be_only_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Description cannot be only whitespace")
        return v.strip()

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "credit_card_id": 1,
                "category_id": 2,
                "purchase_date": "2025-01-15",
                "description": "Laptop Dell XPS 15",
                "total_amount": "120000.00",
                "currency": "ARS",
                "installments_count": 12,
            }
        },
    )


class PurchaseResponseDTO(BaseModel):
    """Response DTO for Purchase"""

    id: int
    user_id: int
    credit_card_id: int
    category_id: int
    purchase_date: date
    description: str
    total_amount: Decimal
    currency: Currency
    installments_count: int

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 10,
                "credit_card_id": 1,
                "category_id": 2,
                "purchase_date": "2025-01-15",
                "description": "Laptop Dell XPS 15",
                "total_amount": "120000.00",
                "currency": "ARS",
                "installments_count": 12,
            }
        },
    )


class InstallmentResponseDTO(BaseModel):
    """Response DTO for Installment (read-only)"""

    id: int
    purchase_id: int
    installment_number: int
    total_installments: int
    amount: Decimal
    currency: Currency
    billing_period: str
    manually_assigned_statement_id: int | None

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "purchase_id": 1,
                "installment_number": 1,
                "total_installments": 12,
                "amount": "10000.00",
                "currency": "ARS",
                "billing_period": "202502",
                "due_date": "2025-02-20",
                "manually_assigned_statement_id": 14,
            }
        },
    )


class CreateCreditCardInputDTO(BaseModel):
    """Input DTO for credit card creation"""

    name: str = Field(min_length=1, max_length=100, description="Card nickname")
    bank: str = Field(min_length=1, max_length=100, description="Bank name")
    last_four_digits: str = Field(
        min_length=4, max_length=4, pattern=r"^\d{4}$", description="Last 4 digits"
    )
    billing_close_day: int = Field(
        ge=1, le=31, description="Billing cycle close day (1-31)"
    )
    payment_due_day: int = Field(ge=1, le=31, description="Payment due day (1-31)")
    credit_limit_amount: Decimal | None = Field(
        default=None, gt=0, description="Credit limit amount (optional)"
    )
    credit_limit_currency: Currency | None = Field(
        default=None, description="Credit limit currency (optional)"
    )

    @field_validator("name", "bank")
    @classmethod
    def string_must_not_be_only_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be only whitespace")
        return v.strip()

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "name": "Visa Gold",
                "bank": "HSBC",
                "last_four_digits": "1234",
                "billing_close_day": 10,
                "payment_due_day": 20,
                "credit_limit_amount": "500000.00",
                "credit_limit_currency": "ARS",
            }
        },
    )


class CreditCardResponseDTO(BaseModel):
    """Response DTO for Credit Card"""

    id: int
    user_id: int
    name: str
    bank: str
    last_four_digits: str
    billing_close_day: int
    payment_due_day: int
    credit_limit_amount: Decimal | None
    credit_limit_currency: Currency | None

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 10,
                "name": "Visa Gold",
                "bank": "HSBC",
                "last_four_digits": "1234",
                "billing_close_day": 10,
                "payment_due_day": 20,
                "credit_limit_amount": "500000.00",
                "credit_limit_currency": "ARS",
            }
        },
    )


class CategoryResponseDTO(BaseModel):
    """Response DTO for Category"""

    id: int
    name: str
    color: str | None
    icon: str | None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Electronics",
                "color": "#FF5733",
                "icon": "laptop",
            }
        },
    )


class CreditCardSummaryResponseDTO(BaseModel):
    """Response DTO for Credit Card Summary"""

    credit_card_id: int
    billing_period: str
    total_amount: Decimal
    currency: Currency
    installments_count: int
    installments: list[InstallmentResponseDTO]

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "credit_card_id": 1,
                "billing_period": "202501",
                "total_amount": "35000.00",
                "currency": "ARS",
                "installments_count": 3,
                "installments": [
                    {
                        "id": 1,
                        "purchase_id": 1,
                        "installment_number": 1,
                        "total_installments": 12,
                        "amount": "10000.00",
                        "currency": "ARS",
                        "billing_period": "202501",
                        "due_date": "2025-02-20",
                    }
                ],
            }
        },
    )


class UpdatePurchaseInputDTO(BaseModel):
    credit_card_id: int = Field(gt=0, description="Credit card ID")
    category_id: int | None = Field(gt=0, description="Category ID")
    purchase_date: date | None = Field(description="Date of purchase")
    description: str | None = Field(
        min_length=1, max_length=500, description="Purchase description"
    )
    total_amount: Decimal = Field(
        description="Total purchase amount (positive for purchases, negative for credits)"
    )

    @field_validator("description")
    @classmethod
    def description_must_not_be_only_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Description cannot be only whitespace")
        return v.strip()

    model_config = ConfigDict(
        use_enum_values=True,
    )
