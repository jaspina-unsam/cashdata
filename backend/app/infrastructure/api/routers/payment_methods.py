from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.application.use_cases.list_credit_cards_by_user_use_case import (
    ListCreditCardsByUserUseCase,
    ListCreditCardsByUserQuery,
)
from app.application.dtos.purchase_dto import (
    CreditCardResponseDTO,
)
from app.application.mappers.purchase_dto_mapper import (
    CreditCardDTOMapper,
)
from app.domain.repositories import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work


router = APIRouter(prefix="/api/v1/payment-methods", tags=["payment-methods"])


@router.get(
    "/{payment_method_id}",
    summary="Get payment method by ID",
    responses={
        200: {"description": "Payment method found"},
        404: {"description": "Payment method not found"},
    },
)
def get_payment_method(
    payment_method_id: int,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Retrieve a specific payment method by ID.

    Only returns the payment method if it belongs to the authenticated user.
    """
    with uow:
        payment_method = uow.payment_methods.find_by_id(payment_method_id)

    if not payment_method or payment_method.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment method with ID {payment_method_id} not found",
        )

    # For now, return basic info. TODO: Create proper PaymentMethod DTO
    return {
        "id": payment_method.id,
        "user_id": payment_method.user_id,
        "type": payment_method.type.value,
        "name": payment_method.name,
        "is_active": payment_method.is_active,
    }