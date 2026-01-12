from typing import List
from app.application.dtos.cash_account_dto import (
    CashAccountResponseDTO,
    CreateCashAccountInputDTO,
)
from app.application.exceptions.application_exceptions import UserNotFoundError
from app.application.mappers.cash_account_mapper import CashAccountDTOMapper
from app.application.use_cases.create_cash_account_use_case import (
    CreateCashAccountUseCase,
)
from app.application.use_cases.delete_cash_account_use_case import (
    DeleteCashAccountUseCase,
)
from app.application.use_cases.list_cash_accounts_use_case import (
    ListAllCashAccountsUseCase,
)
from app.application.use_cases.list_cash_accounts_by_user_id_use_case import (
    ListCashAccountsByUserIdUseCase,
)
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)


router = APIRouter(prefix="/api/v1/cash-accounts", tags=["cash-accounts"])


@router.post(
    "",
    response_model=CashAccountResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cash account",
    responses={
        201: {"description": "Cash account created successfully"},
        400: {"description": "Invalid input data"},
        404: {"description": "User not found"},
    },
)
def create_cash_account(
    cash_account_data: CreateCashAccountInputDTO,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Create a new cash account for a specified user.

    Cash accounts represent physical cash holdings for users.
    
    The user_id is explicitly specified in the request body, which allows for
    scenarios where someone manages finances for another person (e.g., parents
    for children, accountants for clients, or financial tutors).
    
    **Note:** In a production environment with authentication, ensure proper
    authorization checks to verify the requesting user has permission to create
    accounts for the specified user_id.

    Args:
        cash_account_data: Data required to create a cash account, including user_id
        uow: Unit of Work for database operations
    
    Raises:
        404: If the specified user_id does not exist
        400: If validation fails or cash account with currency already exists
    """
    try:
        use_case = CreateCashAccountUseCase(uow)
        cash_account = use_case.execute(cash_account_data)
        return CashAccountDTOMapper.to_response_dto(cash_account)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "",
    response_model=List[CashAccountResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="List all cash accounts",
    responses={
        200: {"description": "List of cash accounts retrieved successfully"},
        400: {"description": "Invalid request"},
    },
)
def list_cash_accounts(
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List all cash accounts.

    Args:
        uow: Unit of Work for database operations
    Returns:
        List of CashAccountResponseDTO
    """
    try:
        use_case = ListAllCashAccountsUseCase(uow)
        cash_accounts = use_case.execute()
        return cash_accounts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/user/{user_id}",
    response_model=List[CashAccountResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="List all cash accounts for a specific user",
    responses={
        200: {
            "description": "List of cash accounts for the user retrieved successfully"
        },
        400: {"description": "Invalid request"},
    },
)
def list_cash_accounts_by_user_id(
    user_id: int,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List all cash accounts for a specific user.

    Args:
        user_id: ID of the user whose cash accounts to retrieve
        uow: Unit of Work for database operations
    Returns:
        List of CashAccountResponseDTO
    """
    try:
        use_case = ListCashAccountsByUserIdUseCase(uow)
        cash_accounts = use_case.execute(user_id)
        return cash_accounts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{cash_account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a cash account by ID",
    responses={
        204: {"description": "Cash account deleted successfully"},
        400: {"description": "Invalid request"},
        404: {"description": "Cash account not found"},
    },
)
def delete_cash_account(
    cash_account_id: int,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Delete a cash account by its ID.

    Args:
        cash_account_id: ID of the cash account to delete
        uow: Unit of Work for database operations
    """
    try:
        use_case = DeleteCashAccountUseCase(uow)
        use_case.execute(cash_account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
