from typing import List
from app.application.dtos.bank_account_dto import (
    BankAccountResponseDTO,
    CreateBankAccountInputDTO,
)
from app.application.exceptions.application_exceptions import UserNotFoundError
from app.application.mappers.bank_account_mapper import BankAccountDTOMapper
from app.application.use_cases.create_bank_account_use_case import (
    CreateBankAccountUseCase,
)
from app.application.use_cases.list_bank_accounts_by_user_id import (
    ListBankAccountsUseCase,
)
from app.domain.exceptions.domain_exceptions import (
    BankAccountNameError,
    BankAccountUserError,
)
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

router = APIRouter(prefix="/api/v1/bank-accounts", tags=["bank-accounts"])


@router.post(
    "",
    response_model=BankAccountResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bank account",
    responses={
        201: {"description": "Bank account created successfully"},
        400: {"description": "Invalid input data"},
        404: {"description": "User not found"},
    },
)
def create_bank_account(
    bank_account_data: CreateBankAccountInputDTO,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Create a new bank account with one or two owners.

    Bank accounts can have a primary user and an optional secondary user for
    joint accounts (e.g., spouses, family members).
    
    The primary_user_id and optional secondary_user_id are explicitly specified
    in the request body, which allows for scenarios where someone manages finances
    for another person or creates joint accounts.
    
    **Note:** In a production environment with authentication, ensure proper
    authorization checks to verify the requesting user has permission to create
    accounts for the specified user_id(s).

    Args:
        bank_account_data: Data required to create a bank account, including
                           primary_user_id and optional secondary_user_id
        uow: Unit of Work for database operations
    
    Raises:
        404: If either primary_user_id or secondary_user_id does not exist
        400: If validation fails (e.g., primary == secondary, invalid name)
    """
    try:
        use_case = CreateBankAccountUseCase(uow)
        bank_account = use_case.execute(bank_account_data)
        return BankAccountDTOMapper.to_response_dto(bank_account)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ValueError, BankAccountNameError, BankAccountUserError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "",
    response_model=List[BankAccountResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="List bank accounts by user ID",
    responses={
        200: {"description": "List of bank accounts for the user"},
        400: {"description": "Invalid user ID"},
    },
)
def list_bank_accounts_by_user_id(
    user_id: int,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List all bank accounts associated with a given user ID.

    Args:
        user_id: ID of the user whose bank accounts are to be retrieved
        uow: Unit of Work for database operations
    """
    try:
        use_case = ListBankAccountsUseCase(uow)
        bank_accounts = use_case.execute(user_id)
        return [BankAccountDTOMapper.to_response_dto(ba) for ba in bank_accounts]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
