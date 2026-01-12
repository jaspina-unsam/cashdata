from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.digital_wallet_dto import (
    CreateDigitalWalletInputDTO,
    DigitalWalletResponseDTO,
)
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


@router.post("", response_model=DigitalWalletResponseDTO, status_code=status.HTTP_201_CREATED)
def create_digital_wallet(
    wallet_data: CreateDigitalWalletInputDTO,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    try:
        use_case = CreateDigitalWalletUseCase(uow)
        created = use_case.execute(wallet_data)
        return DigitalWalletDTOMapper.to_response_dto(created)
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
