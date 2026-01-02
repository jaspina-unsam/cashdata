from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import date

from cashdata.application.use_cases.create_purchase_use_case import (
    CreatePurchaseUseCase,
    CreatePurchaseCommand,
)
from cashdata.application.use_cases.get_purchase_by_id_use_case import (
    GetPurchaseByIdUseCase,
    GetPurchaseByIdQuery,
)
from cashdata.application.use_cases.list_purchases_by_user_use_case import (
    ListPurchasesByUserUseCase,
    ListPurchasesByUserQuery,
)
from cashdata.application.use_cases.list_purchases_by_date_range_use_case import (
    ListPurchasesByDateRangeUseCase,
    ListPurchasesByDateRangeQuery,
)
from cashdata.application.use_cases.list_installments_by_purchase_use_case import (
    ListInstallmentsByPurchaseUseCase,
    ListInstallmentsByPurchaseQuery,
)
from cashdata.application.dtos.purchase_dto import (
    CreatePurchaseInputDTO,
    PurchaseResponseDTO,
    InstallmentResponseDTO,
)
from cashdata.application.mappers.purchase_dto_mapper import (
    PurchaseDTOMapper,
    InstallmentDTOMapper,
)
from cashdata.domain.repositories import IUnitOfWork
from cashdata.infrastructure.api.dependencies import get_unit_of_work


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
    }
)
def create_purchase(
    purchase_data: CreatePurchaseInputDTO,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work)
):
    """
    Create a new purchase with automatic installment generation.
    
    - **credit_card_id**: ID of the credit card to use
    - **category_id**: ID of the category for this purchase
    - **purchase_date**: Date of the purchase
    - **description**: Description of the purchase
    - **total_amount**: Total amount of the purchase
    - **currency**: Currency (ARS, USD, etc.)
    - **installments_count**: Number of installments (minimum 1)
    
    The system will automatically generate installments based on:
    - Credit card billing cycle
    - Purchase date
    - Total amount divided evenly (first installment absorbs remainder)
    """
    try:
        command = CreatePurchaseCommand(
            user_id=user_id,
            credit_card_id=purchase_data.credit_card_id,
            category_id=purchase_data.category_id,
            purchase_date=purchase_data.purchase_date,
            description=purchase_data.description,
            total_amount=purchase_data.total_amount,
            currency=purchase_data.currency,
            installments_count=purchase_data.installments_count
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
                detail="Purchase created but could not be retrieved"
            )
        
        return PurchaseDTOMapper.to_response_dto(purchase)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{purchase_id}",
    response_model=PurchaseResponseDTO,
    summary="Get purchase by ID",
    responses={
        200: {"description": "Purchase found"},
        404: {"description": "Purchase not found"},
    }
)
def get_purchase(
    purchase_id: int,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work)
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
            detail=f"Purchase with ID {purchase_id} not found"
        )
    
    return PurchaseDTOMapper.to_response_dto(purchase)


@router.get(
    "",
    response_model=List[PurchaseResponseDTO],
    summary="List purchases for user",
    responses={
        200: {"description": "List of purchases (may be empty)"},
        400: {"description": "Invalid date range"},
    }
)
def list_purchases(
    user_id: int = Query(..., description="User ID (from auth context)"),
    start_date: Optional[date] = Query(None, description="Filter by start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (inclusive)"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    uow: IUnitOfWork = Depends(get_unit_of_work)
):
    """
    List purchases for the authenticated user.
    
    Supports:
    - Date range filtering (start_date and end_date)
    - Pagination (skip and limit)
    
    Returns purchases sorted by date (most recent first).
    """
    try:
        # Use date range filter if provided
        if start_date and end_date:
            query = ListPurchasesByDateRangeQuery(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            use_case = ListPurchasesByDateRangeUseCase(uow)
            purchases = use_case.execute(query)
        else:
            query = ListPurchasesByUserQuery(user_id=user_id)
            use_case = ListPurchasesByUserUseCase(uow)
            purchases = use_case.execute(query)
        
        # Apply pagination
        paginated_purchases = purchases[skip:skip + limit]
        
        return [PurchaseDTOMapper.to_response_dto(p) for p in paginated_purchases]
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{purchase_id}/installments",
    response_model=List[InstallmentResponseDTO],
    summary="List installments for purchase",
    responses={
        200: {"description": "List of installments"},
        400: {"description": "Purchase doesn't belong to user"},
        404: {"description": "Purchase not found"},
    }
)
def list_installments_by_purchase(
    purchase_id: int,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work)
):
    """
    List all installments for a specific purchase.
    
    Returns installments sorted by installment number (1, 2, 3, ...).
    Only returns installments if purchase belongs to the authenticated user.
    """
    try:
        query = ListInstallmentsByPurchaseQuery(purchase_id=purchase_id, user_id=user_id)
        use_case = ListInstallmentsByPurchaseUseCase(uow)
        installments = use_case.execute(query)
        
        return [InstallmentDTOMapper.to_response_dto(inst) for inst in installments]
        
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
