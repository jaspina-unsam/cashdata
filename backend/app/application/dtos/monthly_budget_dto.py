from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal


class CreateMonthlyBudgetCommand(BaseModel):
    """Command DTO for creating a monthly budget"""

    name: str = Field(min_length=1, max_length=100, description="Budget name")
    description: Optional[str] = Field(None, max_length=500, description="Optional budget description")
    created_by_user_id: int = Field(gt=0, description="ID of user creating the budget")
    participant_user_ids: List[int] = Field(min_length=1, description="List of participant user IDs")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "January 2026 Budget",
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
                "description": "Shared budget for household expenses",
                "status": "active",
                "created_by_user_id": 1,
                "participant_count": 2,
                "created_at": "2026-01-01T12:00:00",
                "updated_at": None
            }
        },
    )


class BudgetExpenseDTO(BaseModel):
    """DTO for Budget Expense"""
    id: int
    budget_id: int
    purchase_id: Optional[int]
    installment_id: Optional[int]
    paid_by_user_id: int
    paid_by_user_name: Optional[str]
    snapshot_description: str
    snapshot_amount: Decimal
    snapshot_currency: str
    snapshot_date: str  # ISO date format
    split_type: str


class BudgetExpenseResponsibilityDTO(BaseModel):
    """DTO for Budget Expense Responsibility"""
    id: int
    budget_expense_id: int
    user_id: int
    user_name: Optional[str]
    percentage: Decimal
    responsible_amount: Decimal
    currency: str


class BudgetBalanceDTO(BaseModel):
    """DTO for Budget Balance"""
    user_id: int
    user_name: str
    paid: Decimal
    responsible: Decimal
    balance: Decimal  # positive = owed, negative = owes
    currency: str


class BudgetDebtDTO(BaseModel):
    """DTO for Budget Debt"""
    from_user_id: int
    from_user_name: str
    to_user_id: int
    to_user_name: str
    amount: Decimal
    currency: str


class BudgetDetailsDTO(BaseModel):
    """Complete budget details with expenses, responsibilities, and balances"""
    budget: MonthlyBudgetResponseDTO
    expenses: List[BudgetExpenseDTO]
    responsibilities: Dict[int, List[BudgetExpenseResponsibilityDTO]]  # expense_id -> responsibilities[]
    balances: List[BudgetBalanceDTO]
    debt_summary: List[BudgetDebtDTO]