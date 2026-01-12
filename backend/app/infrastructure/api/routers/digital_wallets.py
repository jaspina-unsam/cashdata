from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.digital_wallet_dto import (
    CreateDigitalWalletInputDTO,
    DigitalWalletResponseDTO,
)
from app.application.exceptions.application_exceptions import UserNotFoundError
from app.application.mappers.digital_wallet_mapper import DigitalWalletDTOMapper
from app.application.use_cases.create_digital_wallet_use_case import (
    CreateDigitalWalletUseCase,
)
from app.application.use_cases.list_digital_wallets_by_user_use_case import (
    ListDigitalWalletsByUserUseCase,
)
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work


router = APIRouter(prefix="/api/v1/digital-wallets", tags=["digital-wallets"])


@router.post(
    "",
    response_model=DigitalWalletResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new digital wallet",
    responses={
        201: {"description": "Digital wallet created successfully"},
        400: {"description": "Invalid input data"},
        404: {"description": "User not found"},
    },
)
def create_digital_wallet(
    wallet_data: CreateDigitalWalletInputDTO,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Create a new digital wallet for a specified user.

    Digital wallets represent virtual payment methods like MercadoPago, PersonalPay, etc.
    
    The user_id is explicitly specified in the request body, which allows for
    scenarios where someone manages finances for another person (e.g., parents
    for children, accountants for clients, or financial tutors).
    
    **Note:** In a production environment with authentication, ensure proper
    authorization checks to verify the requesting user has permission to create
    wallets for the specified user_id.

    Args:
        wallet_data: Data required to create a digital wallet, including user_id
        uow: Unit of Work for database operations
    
    Raises:
        404: If the specified user_id does not exist
        400: If validation fails (e.g., invalid provider)
    """
    try:
        use_case = CreateDigitalWalletUseCase(uow)
        created = use_case.execute(wallet_data)
        return DigitalWalletDTOMapper.to_response_dto(created)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/user/{user_id}", response_model=List[DigitalWalletResponseDTO], status_code=status.HTTP_200_OK)
def list_digital_wallets_by_user(user_id: int, uow: IUnitOfWork = Depends(get_unit_of_work)):
    try:
        use_case = ListDigitalWalletsByUserUseCase(uow)
        wallets = use_case.execute(user_id)
        # Map to response DTOs
        return [DigitalWalletDTOMapper.to_response_dto(w) for w in wallets]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
