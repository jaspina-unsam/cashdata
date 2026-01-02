from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from cashdata.application.use_cases.get_credit_card_summary_use_case import (
    GetCreditCardSummaryUseCase,
    GetCreditCardSummaryQuery,
)
from cashdata.application.use_cases.list_credit_cards_by_user_use_case import (
    ListCreditCardsByUserUseCase,
    ListCreditCardsByUserQuery,
)
from cashdata.application.use_cases.list_purchases_by_credit_card_use_case import (
    ListPurchasesByCreditCardUseCase,
    ListPurchasesByCreditCardQuery,
)
from cashdata.application.dtos.purchase_dto import (
    CreateCreditCardInputDTO,
    CreditCardResponseDTO,
    CreditCardSummaryResponseDTO,
    PurchaseResponseDTO,
)
from cashdata.application.mappers.purchase_dto_mapper import (
    CreditCardDTOMapper,
    CreditCardSummaryDTOMapper,
    PurchaseDTOMapper,
)
from cashdata.domain.entities.tarjeta_credito import CreditCard
from cashdata.domain.value_objects.money import Money
from cashdata.domain.repositories import IUnitOfWork
from cashdata.infrastructure.api.dependencies import get_unit_of_work


router = APIRouter(prefix="/api/v1/credit-cards", tags=["credit-cards"])


@router.post(
    "",
    response_model=CreditCardResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new credit card",
    responses={
        201: {"description": "Credit card created successfully"},
        400: {"description": "Invalid input data"},
    },
)
def create_credit_card(
    card_data: CreateCreditCardInputDTO,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Create a new credit card for the user.

    - **name**: Nickname for the card (e.g., "Visa Gold")
    - **bank**: Bank name
    - **last_four_digits**: Last 4 digits of the card
    - **billing_close_day**: Day of month when billing closes (1-31)
    - **payment_due_day**: Day of month when payment is due (1-31)
    - **credit_limit_amount**: Optional credit limit amount
    - **credit_limit_currency**: Optional credit limit currency
    """
    try:
        # Create credit limit Money object if provided
        credit_limit = None
        if (
            card_data.credit_limit_amount is not None
            and card_data.credit_limit_currency is not None
        ):
            credit_limit = Money(
                card_data.credit_limit_amount, card_data.credit_limit_currency
            )

        # Create entity
        credit_card = CreditCard(
            id=None,
            user_id=user_id,
            name=card_data.name,
            bank=card_data.bank,
            last_four_digits=card_data.last_four_digits,
            billing_close_day=card_data.billing_close_day,
            payment_due_day=card_data.payment_due_day,
            credit_limit=credit_limit,
        )

        # Save using UoW
        with uow:
            saved_card = uow.credit_cards.save(credit_card)
            uow.commit()

        return CreditCardDTOMapper.to_response_dto(saved_card)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "",
    response_model=List[CreditCardResponseDTO],
    summary="List all credit cards for user",
    responses={
        200: {"description": "List of credit cards (may be empty)"},
    },
)
def list_credit_cards(
    user_id: int = Query(..., description="User ID (from auth context)"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List all credit cards for the authenticated user.
    
    Supports pagination (skip and limit).
    """
    query = ListCreditCardsByUserQuery(user_id=user_id)
    use_case = ListCreditCardsByUserUseCase(uow)
    credit_cards = use_case.execute(query)
    
    # Apply pagination
    paginated_cards = credit_cards[skip:skip + limit]
    
    return [CreditCardDTOMapper.to_response_dto(card) for card in paginated_cards]


@router.get(
    "/{card_id}",
    response_model=CreditCardResponseDTO,
    summary="Get credit card by ID",
    responses={
        200: {"description": "Credit card found"},
        404: {"description": "Credit card not found or doesn't belong to user"},
    },
)
def get_credit_card(
    card_id: int,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Retrieve a specific credit card by ID.

    Only returns the card if it belongs to the authenticated user.
    """
    with uow:
        credit_card = uow.credit_cards.find_by_id(card_id)

    if not credit_card or credit_card.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credit card with ID {card_id} not found",
        )

    return CreditCardDTOMapper.to_response_dto(credit_card)


@router.get(
    "/{card_id}/summary",
    response_model=CreditCardSummaryResponseDTO,
    summary="Get credit card summary for billing period",
    responses={
        200: {"description": "Summary retrieved successfully"},
        400: {"description": "Invalid billing period format"},
        404: {"description": "Credit card not found"},
    },
)
def get_credit_card_summary(
    card_id: int,
    billing_period: str = Query(
        ...,
        description="Billing period in YYYYMM format (e.g., 202501)",
        regex=r"^\d{6}$",
    ),
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Get a summary of credit card usage for a specific billing period.

    Returns:
    - Total amount due for the period
    - Number of installments
    - List of all installments with details

    Example billing_period: "202501" for January 2025
    """
    try:
        query = GetCreditCardSummaryQuery(
            credit_card_id=card_id, user_id=user_id, billing_period=billing_period
        )

        use_case = GetCreditCardSummaryUseCase(uow)
        summary = use_case.execute(query)

        return CreditCardSummaryDTOMapper.to_response_dto(summary)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{card_id}/purchases",
    response_model=List[PurchaseResponseDTO],
    summary="List purchases for a credit card",
    responses={
        200: {"description": "List of purchases (may be empty)"},
        400: {"description": "Card doesn't belong to user"},
        404: {"description": "Credit card not found"},
    },
)
def list_purchases_by_card(
    card_id: int,
    user_id: int = Query(..., description="User ID (from auth context)"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List all purchases made with a specific credit card.
    
    Returns purchases sorted by date (most recent first).
    Supports pagination (skip and limit).
    Only returns purchases if card belongs to the authenticated user.
    """
    try:
        query = ListPurchasesByCreditCardQuery(credit_card_id=card_id, user_id=user_id)
        use_case = ListPurchasesByCreditCardUseCase(uow)
        purchases = use_case.execute(query)
        
        # Apply pagination
        paginated_purchases = purchases[skip:skip + limit]
        
        return [PurchaseDTOMapper.to_response_dto(p) for p in paginated_purchases]
        
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
