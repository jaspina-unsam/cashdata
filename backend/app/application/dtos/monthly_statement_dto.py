"""Data Transfer Objects for monthly statements."""

from dataclasses import dataclass
from datetime import date


@dataclass
class MonthlyStatementResponseDTO:
    """DTO for monthly statement response."""

    id: int
    credit_card_id: int
    credit_card_name: str
    start_date: date
    closing_date: date
    due_date: date


@dataclass
class UpdateStatementDatesInputDTO:
    """DTO for updating statement dates."""

    start_date: date
    closing_date: date
    due_date: date


@dataclass
class CreateStatementInputDTO:
    """DTO for creating a new statement."""

    credit_card_id: int
    start_date: date
    closing_date: date
    due_date: date


@dataclass
class PurchaseInStatementDTO:
    """DTO for purchase information in statement detail."""

    id: int
    description: str
    purchase_date: date
    amount: float
    currency: str
    installments: int
    installment_number: int | None  # None for full purchases, 1-N for installments
    category_name: str


@dataclass
class StatementDetailDTO:
    """DTO for statement detail with purchases."""

    id: int
    credit_card_id: int
    credit_card_name: str
    start_date: date
    closing_date: date
    due_date: date
    period_start_date: date
    period_end_date: date
    purchases: list[PurchaseInStatementDTO]
    total_amount: float
    currency: str
