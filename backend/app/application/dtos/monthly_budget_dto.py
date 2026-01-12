from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class CreateMonthlyBudgetCommand(BaseModel):
    """Command DTO for creating a monthly budget"""

    name: str = Field(min_length=1, max_length=100, description="Budget name")
    year: int = Field(ge=2020, le=2030, description="Budget year")
    month: int = Field(ge=1, le=12, description="Budget month (1-12)")
    description: Optional[str] = Field(None, max_length=500, description="Optional budget description")
    created_by_user_id: int = Field(gt=0, description="ID of user creating the budget")
    participant_user_ids: List[int] = Field(min_length=1, description="List of participant user IDs")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "January 2026 Budget",
                "year": 2026,
                "month": 1,
                "description": "Shared budget for household expenses",
                "created_by_user_id": 1,
                "participant_user_ids": [1, 2]
            }
        },
    )


class MonthlyBudgetResponseDTO(BaseModel):
    """Response DTO for MonthlyBudget"""

    id: int
    name: str
    period: str  # Formatted as YYYYMM
    description: Optional[str]
    status: str
    created_by_user_id: int
    participant_count: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "January 2026 Budget",
                "period": "202601",
                "description": "Shared budget for household expenses",
                "status": "active",
                "created_by_user_id": 1,
                "participant_count": 2,
                "created_at": "2026-01-01T12:00:00",
                "updated_at": None
            }
        },
    )