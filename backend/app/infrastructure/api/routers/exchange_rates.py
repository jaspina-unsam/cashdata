from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import date

from app.application.use_cases.create_exchange_rate_use_case import (
    CreateExchangeRateUseCase,
    CreateExchangeRateCommand,
)
from app.application.use_cases.list_exchange_rates_use_case import (
    ListExchangeRatesByDateRangeUseCase,
    ListExchangeRatesQuery,
)
from app.application.use_cases.get_latest_exchange_rate_use_case import (
    GetLatestExchangeRateUseCase,
    GetLatestExchangeRateQuery,
)
from app.application.dtos.exchange_rate_dto import (
    CreateExchangeRateInputDTO,
    ExchangeRateResponseDTO,
)
from app.application.exceptions.application_exceptions import ApplicationError
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work


router = APIRouter(prefix="/api/v1/exchange-rates", tags=["exchange-rates"])


@router.post(
    "",
    response_model=ExchangeRateResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new exchange rate",
    responses={
        201: {"description": "Exchange rate created successfully"},
        400: {"description": "Invalid input data or duplicate exchange rate"},
    },
)
def create_exchange_rate(
    rate_data: CreateExchangeRateInputDTO,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Create a new exchange rate.

    - **date**: Date of the exchange rate
    - **from_currency**: Source currency (default: USD)
    - **to_currency**: Target currency (default: ARS)
    - **rate**: Exchange rate value (must be positive)
    - **rate_type**: Type of exchange rate (official, blue, mep, ccl, custom, inferred)
    - **source**: Optional source of the rate
    - **notes**: Optional additional notes
    """
    try:
        command = CreateExchangeRateCommand(
            date=rate_data.date,
            from_currency=rate_data.from_currency,
            to_currency=rate_data.to_currency,
            rate=rate_data.rate,
            rate_type=rate_data.rate_type,
            user_id=user_id,
            source=rate_data.source,
            notes=rate_data.notes,
        )

        use_case = CreateExchangeRateUseCase(uow)
        result = use_case.execute(command)

        # Retrieve the created exchange rate
        exchange_rate = uow.exchange_rates.find_by_id(result.exchange_rate_id)

        if not exchange_rate:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Exchange rate created but could not be retrieved",
            )

        return ExchangeRateResponseDTO(
            id=exchange_rate.id,
            date=exchange_rate.date,
            from_currency=exchange_rate.from_currency,
            to_currency=exchange_rate.to_currency,
            rate=exchange_rate.rate,
            rate_type=exchange_rate.rate_type,
            source=exchange_rate.source,
            notes=exchange_rate.notes,
            created_by_user_id=exchange_rate.created_by_user_id,
            created_at=exchange_rate.created_at,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ApplicationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "",
    response_model=List[ExchangeRateResponseDTO],
    summary="List exchange rates",
    responses={
        200: {"description": "Exchange rates retrieved successfully"},
        400: {"description": "Invalid query parameters"},
    },
)
def list_exchange_rates(
    start_date: date = Query(..., description="Start date for filtering"),
    end_date: date = Query(..., description="End date for filtering"),
    from_currency: Optional[str] = Query(None, description="Filter by source currency"),
    to_currency: Optional[str] = Query(None, description="Filter by target currency"),
    rate_type: Optional[str] = Query(None, description="Filter by rate type"),
    user_id: Optional[int] = Query(None, description="User ID for custom rates"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List exchange rates within a date range.

    Optional filters:
    - **from_currency**: Filter by source currency
    - **to_currency**: Filter by target currency
    - **rate_type**: Filter by rate type
    - **user_id**: Filter by user (for custom rates)
    """
    try:
        query = ListExchangeRatesQuery(
            start_date=start_date,
            end_date=end_date,
            from_currency=from_currency,
            to_currency=to_currency,
            rate_type=rate_type,
            user_id=user_id,
        )

        use_case = ListExchangeRatesByDateRangeUseCase(uow)
        result = use_case.execute(query)

        return [
            ExchangeRateResponseDTO(
                id=rate.id,
                date=rate.date,
                from_currency=rate.from_currency,
                to_currency=rate.to_currency,
                rate=rate.rate,
                rate_type=rate.rate_type,
                source=rate.source,
                notes=rate.notes,
                created_by_user_id=rate.created_by_user_id,
                created_at=rate.created_at,
            )
            for rate in result.exchange_rates
        ]

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/latest",
    response_model=ExchangeRateResponseDTO,
    summary="Get latest exchange rate",
    responses={
        200: {"description": "Latest exchange rate retrieved successfully"},
        404: {"description": "No exchange rate found"},
        400: {"description": "Invalid query parameters"},
    },
)
def get_latest_exchange_rate(
    from_currency: str = Query("USD", description="Source currency"),
    to_currency: str = Query("ARS", description="Target currency"),
    rate_type: str = Query(..., description="Rate type"),
    reference_date: Optional[date] = Query(None, description="Reference date (default: today)"),
    user_id: Optional[int] = Query(None, description="User ID for custom rates"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Get the latest exchange rate for a given type.

    - **rate_type**: Type of exchange rate (official, blue, mep, ccl, custom)
    - **reference_date**: Optional reference date (default: today)
    """
    try:
        query = GetLatestExchangeRateQuery(
            from_currency=from_currency,
            to_currency=to_currency,
            rate_type=rate_type,
            reference_date=reference_date,
            user_id=user_id,
        )

        use_case = GetLatestExchangeRateUseCase(uow)
        result = use_case.execute(query)

        if not result.exchange_rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No exchange rate found for type {rate_type}",
            )

        rate = result.exchange_rate
        return ExchangeRateResponseDTO(
            id=rate.id,
            date=rate.date,
            from_currency=rate.from_currency,
            to_currency=rate.to_currency,
            rate=rate.rate,
            rate_type=rate.rate_type,
            source=rate.source,
            notes=rate.notes,
            created_by_user_id=rate.created_by_user_id,
            created_at=rate.created_at,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{rate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an exchange rate",
    responses={
        204: {"description": "Exchange rate deleted successfully"},
        404: {"description": "Exchange rate not found"},
    },
)
def delete_exchange_rate(
    rate_id: int,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """Delete an exchange rate by its ID."""
    try:
        with uow:
            # Check if rate exists
            rate = uow.exchange_rates.find_by_id(rate_id)
            if not rate:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Exchange rate with ID {rate_id} not found",
                )

            # Delete the rate
            uow.exchange_rates.delete(rate_id)
            uow.commit()

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
