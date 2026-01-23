from datetime import date as date_type, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CreateExchangeRateInputDTO(BaseModel):
    """Input DTO for creating an exchange rate"""

    date: date_type = Field(description="Date of the exchange rate")
    from_currency: str = Field(default="USD", description="Source currency")
    to_currency: str = Field(default="ARS", description="Target currency")
    rate: Decimal = Field(gt=0, description="Exchange rate (must be positive)")
    rate_type: str = Field(description="Type of exchange rate")
    source: Optional[str] = Field(None, max_length=100, description="Source of the rate")
    notes: Optional[str] = Field(None, description="Additional notes")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2026-01-23",
                "from_currency": "USD",
                "to_currency": "ARS",
                "rate": "1500.00",
                "rate_type": "blue",
                "source": "Dolar Blue",
                "notes": "Cotización del dólar blue"
            }
        },
    )


class ExchangeRateResponseDTO(BaseModel):
    """Response DTO for Exchange Rate"""

    id: int
    date: date_type
    from_currency: str
    to_currency: str
    rate: Decimal
    rate_type: str
    source: Optional[str]
    notes: Optional[str]
    created_by_user_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "date": "2026-01-23",
                "from_currency": "USD",
                "to_currency": "ARS",
                "rate": "1500.00",
                "rate_type": "blue",
                "source": "Dolar Blue",
                "notes": "Cotización del dólar blue",
                "created_by_user_id": 1,
                "created_at": "2026-01-23T10:30:00"
            }
        },
    )
