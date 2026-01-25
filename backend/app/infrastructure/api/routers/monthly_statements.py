"""API router for monthly statements."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.dtos.monthly_statement_dto import (
    CreateStatementInputDTO,
    MonthlyStatementResponseDTO,
    StatementDetailDTO,
    UpdateStatementDatesInputDTO,
)
from app.application.use_cases.create_statement_use_case import (
    CreateStatementUseCase,
)
from app.application.use_cases.get_statement_detail_use_case import (
    GetStatementDetailUseCase,
)
from app.application.use_cases.list_monthly_statements_use_case import (
    ListMonthlyStatementsUseCase,
)
from app.application.use_cases.list_statements_by_credit_card_use_case import (
    ListStatementByCreditCardUseCase,
    ListStatementByCreditCardQuery,
)
from app.application.use_cases.update_statement_dates_use_case import (
    UpdateStatementDatesUseCase,
)
from app.application.use_cases.delete_statement_use_case import (
    DeleteStatementUseCase,
    DeleteStatementCommand,
)
from app.application.exceptions.application_exceptions import (
    CreditCardNotFoundError,
    CreditCardOwnerMismatchError,
    MonthlyStatementNotFoundError,
    BusinessRuleViolationError,
)
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work
from fastapi import Response

router = APIRouter(prefix="/api/v1/statements", tags=["statements"])


@router.get(
    "",
    response_model=List[MonthlyStatementResponseDTO],
    summary="List monthly statements for a user",
    responses={
        200: {"description": "List of monthly statements"},
        400: {"description": "Invalid user_id parameter"},
    },
)
def list_statements(
    user_id: int = Query(..., description="User ID"),
    include_future: bool = Query(
        False, description="Include statements with future payment dates"
    ),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """List all monthly statements for a user's credit cards.

    Statements are returned ordered by due_date descending (most recent first).
    By default, only past statements (due_date <= today) are included.
    """
    with uow:
        use_case = ListMonthlyStatementsUseCase(
            uow.monthly_statements, uow.credit_cards
        )
        return use_case.execute(user_id, include_future)


@router.get(
    "/{statement_id}",
    response_model=StatementDetailDTO,
    summary="Get statement detail with purchases",
    responses={
        200: {"description": "Statement detail with all purchases"},
        404: {"description": "Statement not found or not authorized"},
    },
)
def get_statement_detail(
    statement_id: int,
    user_id: int = Query(..., description="User ID for authorization"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """Get statement detail including all purchases and installments in the period.

    The response includes:
    - Statement dates (billing close, payment due)
    - Period range (start date, end date)
    - All purchases that fall within the statement period
    - Individual installments for multi-installment purchases
    """
    with uow:
        use_case = GetStatementDetailUseCase(
            uow.monthly_statements,
            uow.credit_cards,
            uow.purchases,
            uow.categories,
            uow.installments,
        )
        result = use_case.execute(statement_id, user_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Statement not found or you don't have access to it",
            )

        return result


@router.post(
    "",
    response_model=MonthlyStatementResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new monthly statement",
    responses={
        201: {"description": "Statement created successfully"},
        400: {"description": "Invalid input data or credit card not found"},
    },
)
def create_statement(
    statement_data: CreateStatementInputDTO,
    user_id: int = Query(..., description="User ID for authorization"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """Create a new monthly statement for a credit card.

    The closing_date must be on or before the due_date.
    The credit card must exist and belong to the specified user.
    """
    with uow:
        use_case = CreateStatementUseCase(uow.monthly_statements, uow.credit_cards)
        try:
            result = use_case.execute(user_id, statement_data)
            uow.commit()
            return result
        except ValueError as e:
            uow.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )


@router.put(
    "/{statement_id}",
    response_model=MonthlyStatementResponseDTO,
    summary="Update statement dates",
    responses={
        200: {"description": "Statement dates updated successfully"},
        400: {"description": "Invalid dates (close_date > due_date)"},
        404: {"description": "Statement not found or not authorized"},
    },
)
def update_statement_dates(
    statement_id: int,
    dates_data: UpdateStatementDatesInputDTO,
    user_id: int = Query(..., description="User ID for authorization"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """Update billing close date and payment due date for a statement.

    When dates are updated, the statement period changes which may affect
    which purchases belong to this statement. The frontend should refresh
    the statement detail after this operation.

    The closing_date must be on or before the due_date.
    """
    with uow:
        use_case = UpdateStatementDatesUseCase(
            uow.monthly_statements, uow.credit_cards, uow.purchases, uow.installments
        )
        try:
            result = use_case.execute(statement_id, user_id, dates_data)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Statement not found or you don't have access to it",
                )
            uow.commit()
            return result
        except ValueError as e:
            uow.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )


@router.get(
    "/by-card/{credit_card_id}",
    response_model=List[MonthlyStatementResponseDTO],
    summary="List monthly statements for a credit card",
    responses={
        200: {"description": "List of monthly statements for the credit card"},
        404: {"description": "Credit card not found or not authorized"},
    },
)
def list_statements_by_card(
    credit_card_id: int,
    user_id: int = Query(..., description="User ID for authorization"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List all monthly statements for a specific credit card.

    Used for dropdowns when manually assigning installments to statements.
    Only returns statements for credit cards owned by the authenticated user.
    """
    with uow:
        use_case = ListStatementByCreditCardUseCase(uow)
        query = ListStatementByCreditCardQuery(
            user_id=user_id,
            credit_card_id=credit_card_id,
        )
        try:
            return use_case.execute(query)
        except (CreditCardNotFoundError, CreditCardOwnerMismatchError) as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )


@router.delete(
    "/{statement_id}",
    summary="Delete statement",
    responses={
        204: {"description": "Statement deleted successfully"},
        404: {"description": "Statement not found"},
        403: {"description": "Forbidden - Statement does not belong to user"},
        422: {"description": "Business rule violation"},
    },
)
def delete_statement(
    statement_id: int,
    user_id: int = Query(..., description="User ID for authorization"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Permanently delete a monthly statement.

    Business rules:
    - Statement must exist
    - Statement must belong to a credit card owned by the user
    """
    try:
        use_case = DeleteStatementUseCase(uow)
        command = DeleteStatementCommand(statement_id=statement_id, user_id=user_id)
        use_case.execute(command)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except MonthlyStatementNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")
    except CreditCardOwnerMismatchError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Statement does not belong to user")
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}")
