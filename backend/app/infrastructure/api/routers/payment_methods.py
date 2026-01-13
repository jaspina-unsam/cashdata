from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.application.use_cases.list_payment_methods_by_user_id_use_case import (
    ListPaymentMethodsByUserIdUseCase,
)
from app.application.dtos.payment_method_dto import (
    PaymentMethodResponseDTO,
)
from app.application.mappers.payment_method_mapper import (
    PaymentMethodDTOMapper,
)
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work


router = APIRouter(prefix="/api/v1/payment-methods", tags=["payment-methods"])


@router.get(
    "",
    response_model=List[PaymentMethodResponseDTO],
    summary="List payment methods",
    responses={
        200: {"description": "List of payment methods (may be empty)"},
    },
)
def list_payment_methods(
    user_id: int = Query(None, description="User ID to filter by (omit to get all users' payment methods)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List payment methods.
    
    - If user_id is provided: returns only that user's payment methods
    - If user_id is omitted: returns ALL payment methods from ALL users
    """
    if user_id:
        use_case = ListPaymentMethodsByUserIdUseCase(uow)
        payment_methods = use_case.execute(user_id)
    else:
        # Return all payment methods from all users
        with uow:
            payment_methods_entities = uow.payment_methods.find_all()
            payment_methods = [
                PaymentMethodDTOMapper.to_response_dto(pm) 
                for pm in payment_methods_entities
            ]

    return payment_methods


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