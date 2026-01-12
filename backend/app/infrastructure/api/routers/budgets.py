from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.application.use_cases.create_monthly_budget_use_case import CreateMonthlyBudgetUseCase
from app.application.use_cases.get_budget_details_use_case import GetBudgetDetailsUseCase
from app.application.use_cases.list_budgets_by_period_use_case import ListBudgetsByPeriodUseCase
from app.application.dtos.monthly_budget_dto import (
    CreateMonthlyBudgetCommand,
    MonthlyBudgetResponseDTO,
)
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work
from app.application.exceptions.application_exceptions import (
    UserNotFoundError,
    BusinessRuleViolationError,
)


router = APIRouter(prefix="/api/v1/budgets", tags=["budgets"])


@router.post(
    "",
    response_model=MonthlyBudgetResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new monthly budget",
    responses={
        201: {"description": "Budget created successfully"},
        400: {"description": "Invalid input data"},
        404: {"description": "Creator or participant user not found"},
        409: {"description": "Business rule violation (duplicate participants, creator not participant, budget already exists)"},
    },
)
def create_budget(
    budget_data: CreateMonthlyBudgetCommand,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Create a new monthly budget with participants.

    - **name**: Budget name (1-100 characters)
    - **year**: Budget year (2020-2030)
    - **month**: Budget month (1-12)
    - **description**: Optional budget description (max 500 characters)
    - **created_by_user_id**: ID of user creating the budget
    - **participant_user_ids**: List of participant user IDs (creator must be included)
    """
    try:
        use_case = CreateMonthlyBudgetUseCase(uow)
        result = use_case.execute(budget_data)
        return result

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except BusinessRuleViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[MonthlyBudgetResponseDTO],
    summary="List budgets by period for user",
    responses={
        200: {"description": "List of budgets returned successfully"},
        400: {"description": "Invalid period format"},
    },
)
def list_budgets(
    period: str = Query(..., description="Period in YYYYMM format", min_length=6, max_length=6),
    user_id: int = Query(..., description="User ID to filter budgets", gt=0),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List all budgets for a specific period where the user is a participant.

    - **period**: Period in YYYYMM format (e.g., "202601")
    - **user_id**: ID of the user to filter budgets
    """
    try:
        use_case = ListBudgetsByPeriodUseCase(uow)
        result = use_case.execute(period, user_id)
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period format: {str(e)}"
        )


@router.get(
    "/{budget_id}",
    response_model=MonthlyBudgetResponseDTO,
    summary="Get budget details",
    responses={
        200: {"description": "Budget details returned successfully"},
        404: {"description": "Budget not found"},
        403: {"description": "User not authorized to view budget"},
    },
)
def get_budget_details(
    budget_id: int,
    user_id: int = Query(..., description="User ID for authorization check", gt=0),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Get complete details of a specific budget.

    - **budget_id**: ID of the budget to retrieve
    - **user_id**: ID of the requesting user (must be a participant)
    """
    try:
        use_case = GetBudgetDetailsUseCase(uow)
        result = use_case.execute(budget_id, user_id)
        return result

    except BusinessRuleViolationError as e:
        # Check if it's a "not found" or "not authorized" error
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg
            )