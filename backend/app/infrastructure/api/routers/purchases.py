from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import date

from app.application.use_cases.create_purchase_use_case import (
    CreatePurchaseUseCase,
    CreatePurchaseCommand,
)
from app.application.use_cases.get_purchase_by_id_use_case import (
    GetPurchaseByIdUseCase,
    GetPurchaseByIdQuery,
)
from app.application.use_cases.list_purchases_by_user_use_case import (
    ListPurchasesByUserUseCase,
    ListPurchasesByUserQuery,
)
from app.application.use_cases.list_purchases_by_date_range_use_case import (
    ListPurchasesByDateRangeUseCase,
    ListPurchasesByDateRangeQuery,
)
from app.application.use_cases.list_purchases_by_payment_method_use_case import (
    ListPurchasesByPaymentMethodUseCase,
    ListPurchasesByPaymentMethodQuery,
)
from app.application.use_cases.list_installments_by_purchase_use_case import (
    ListInstallmentsByPurchaseUseCase,
    ListInstallmentsByPurchaseQuery,
)
from app.application.use_cases.update_purchase_use_case import (
    UpdatePurchaseUseCase,
    UpdatePurchaseCommand,
)
from app.application.use_cases.delete_purchase_use_case import (
    DeletePurchaseUseCase,
)
from app.application.dtos.purchase_dto import (
    CreatePurchaseInputDTO,
    PurchaseResponseDTO,
    InstallmentResponseDTO,
    UpdatePurchaseInputDTO,
    PaginatedResponse,
)
from app.application.mappers.purchase_dto_mapper import (
    PurchaseDTOMapper,
    InstallmentDTOMapper,
)
from app.application.exceptions.application_exceptions import ApplicationError
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work


router = APIRouter(prefix="/api/v1/purchases", tags=["purchases"])


@router.post(
    "",
    response_model=PurchaseResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new purchase",
    responses={
        201: {"description": "Purchase created successfully"},
        400: {"description": "Invalid input data"},
        404: {"description": "Credit card or category not found"},
    },
)
def create_purchase(
    purchase_data: CreatePurchaseInputDTO,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Create a new purchase with automatic installment generation.

    - **payment_method_id**: ID of the payment method to use
    - **category_id**: ID of the category for this purchase
    - **purchase_date**: Date of the purchase
    - **description**: Description of the purchase
    - **total_amount**: Total amount of the purchase
    - **currency**: Currency (ARS, USD, etc.)
    - **installments_count**: Number of installments (minimum 1)

    The system will automatically generate installments based on:
    - Payment method type and billing cycle
    - Purchase date
    - Total amount divided evenly (first installment absorbs remainder)
    """
    try:
        command = CreatePurchaseCommand(
            user_id=user_id,
            payment_method_id=purchase_data.payment_method_id,
            category_id=purchase_data.category_id,
            purchase_date=purchase_data.purchase_date,
            description=purchase_data.description,
            total_amount=purchase_data.total_amount,
            currency=purchase_data.currency,
            installments_count=purchase_data.installments_count,
            original_amount=purchase_data.original_amount,
            original_currency=purchase_data.original_currency,
            rate_type=purchase_data.rate_type,
            exchange_rate_id=purchase_data.exchange_rate_id,
        )

        use_case = CreatePurchaseUseCase(uow)
        result = use_case.execute(command)

        # Retrieve the created purchase to return full data
        query = GetPurchaseByIdQuery(purchase_id=result.purchase_id, user_id=user_id)
        get_use_case = GetPurchaseByIdUseCase(uow)
        purchase = get_use_case.execute(query)

        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Purchase created but could not be retrieved",
            )

        return PurchaseDTOMapper.to_response_dto(purchase)

    except ApplicationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch(
    "/{purchase_id}",
    response_model=PurchaseResponseDTO,
    summary="Update purchase",
    responses={
        200: {"description": "Purchase updated successfully"},
        400: {"description": "Invalid input data or unsupported update"},
        404: {"description": "Purchase, credit card, or category not found"},
    },
)
def update_purchase(
    purchase_id: int,
    purchase_data: UpdatePurchaseInputDTO,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Update an existing purchase.

    Only basic fields can be updated currently (description, category).
    Updating payment_method_id, purchase_date, or total_amount is not yet supported.

    - **payment_method_id**: ID of the payment method (not yet supported)
    - **category_id**: ID of the category
    - **purchase_date**: Date of purchase (not yet supported)
    - **description**: Description of the purchase
    - **total_amount**: Total amount (not yet supported)
    """
    try:
        command = UpdatePurchaseCommand(
            purchase_id=purchase_id,
            user_id=user_id,
            payment_method_id=purchase_data.payment_method_id,
            category_id=purchase_data.category_id,
            purchase_date=purchase_data.purchase_date,
            description=purchase_data.description,
            total_amount=purchase_data.total_amount,
            original_amount=purchase_data.original_amount,
            original_currency=purchase_data.original_currency,
            exchange_rate_id=purchase_data.exchange_rate_id,
        )

        use_case = UpdatePurchaseUseCase(uow)
        result = use_case.execute(command)

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Catch application exceptions
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{purchase_id}",
    response_model=PurchaseResponseDTO,
    summary="Get purchase by ID",
    responses={
        200: {"description": "Purchase found"},
        404: {"description": "Purchase not found"},
    },
)
def get_purchase(
    purchase_id: int,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Retrieve a specific purchase by ID.

    Only returns the purchase if it belongs to the authenticated user.
    """
    query = GetPurchaseByIdQuery(purchase_id=purchase_id, user_id=user_id)
    use_case = GetPurchaseByIdUseCase(uow)
    purchase = use_case.execute(query)

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase with ID {purchase_id} not found",
        )

    return PurchaseDTOMapper.to_response_dto(purchase)


@router.get(
    "",
    response_model=PaginatedResponse[PurchaseResponseDTO],
    summary="List purchases for user",
    responses={
        200: {"description": "Paginated list of purchases"},
        400: {"description": "Invalid date range or pagination parameters"},
    },
)
def list_purchases(
    user_id: int = Query(..., description="User ID (from auth context)"),
    start_date: Optional[date] = Query(
        None, description="Filter by start date (inclusive)"
    ),
    end_date: Optional[date] = Query(
        None, description="Filter by end date (inclusive)"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        50, ge=1, le=200, description="Number of items per page"
    ),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List purchases for the authenticated user with pagination.

    Supports:
    - Date range filtering (start_date and end_date)
    - Pagination (page and page_size)

    Returns purchases sorted by date (most recent first).
    """
    try:
        # Use date range filter if provided
        if start_date and end_date:
            query = ListPurchasesByDateRangeQuery(
                user_id=user_id, start_date=start_date, end_date=end_date
            )
            use_case = ListPurchasesByDateRangeUseCase(uow)
            purchases = use_case.execute(query)
        else:
            query = ListPurchasesByUserQuery(user_id=user_id)
            use_case = ListPurchasesByUserUseCase(uow)
            purchases = use_case.execute(query)

        # Calculate pagination
        total = len(purchases)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        # Apply pagination
        skip = (page - 1) * page_size
        paginated_purchases = purchases[skip : skip + page_size]
        
        items = [PurchaseDTOMapper.to_response_dto(p) for p in paginated_purchases]

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/by-payment-method/{payment_method_id}",
    response_model=List[PurchaseResponseDTO],
    summary="List purchases by payment method",
    responses={
        200: {"description": "List of purchases for the payment method"},
        404: {"description": "Payment method not found"},
    },
)
def list_purchases_by_payment_method(
    payment_method_id: int,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List all purchases for a specific payment method.

    Only returns purchases if the payment method belongs to the authenticated user.
    Returns purchases sorted by date (most recent first).
    """
    try:
        query = ListPurchasesByPaymentMethodQuery(
            payment_method_id=payment_method_id, user_id=user_id
        )
        use_case = ListPurchasesByPaymentMethodUseCase(uow)
        purchases = use_case.execute(query)

        return [PurchaseDTOMapper.to_response_dto(p) for p in purchases]

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{purchase_id}/installments",
    response_model=List[InstallmentResponseDTO],
    summary="List installments for purchase",
    responses={
        200: {"description": "List of installments"},
        400: {"description": "Purchase doesn't belong to user"},
        404: {"description": "Purchase not found"},
    },
)
def list_installments_by_purchase(
    purchase_id: int,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List all installments for a specific purchase.

    Returns installments sorted by installment number (1, 2, 3, ...).
    Only returns installments if purchase belongs to the authenticated user.
    """
    try:
        query = ListInstallmentsByPurchaseQuery(
            purchase_id=purchase_id, user_id=user_id
        )
        use_case = ListInstallmentsByPurchaseUseCase(uow)
        installments = use_case.execute(query)

        return [InstallmentDTOMapper.to_response_dto(inst) for inst in installments]

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{purchase_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete purchase (soft delete)",
    responses={
        204: {"description": "Purchase and its installments deleted successfully"},
        404: {"description": "Purchase not found"},
    },
)
def delete_purchase(
    purchase_id: int,
    user_id: int = Query(..., description="User ID who owns the purchase"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Soft delete a purchase and all its installments.

    - **purchase_id**: The ID of the purchase to delete
    - **user_id**: The ID of the user who owns the purchase
    """
    try:
        use_case = DeletePurchaseUseCase(uow)
        use_case.execute(purchase_id, user_id)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the exception here if logging is set up
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while deleting the purchase")
