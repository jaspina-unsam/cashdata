from app.application.dtos.purchase_dto import (
    InstallmentResponseDTO,
    UpdateInstallmentInputDTO,
)
from app.application.use_cases.update_installment_use_case import (
    UpdateInstallmentUseCase,
    UpdateInstallmentCommand,
)
from app.application.use_cases.delete_installment_use_case import (
    DeleteInstallmentUseCase,
    DeleteInstallmentCommand,
)
from app.application.exceptions.application_exceptions import (
    InstallmentNotFoundError,
    PurchaseNotFoundError,
    MonthlyStatementNotFoundError,
    BusinessRuleViolationError,
)
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work
from fastapi import APIRouter, Depends, HTTPException, Query


router = APIRouter(prefix="/api/v1/installments", tags=["installments"])


@router.patch(
    "/{installment_id}",
    response_model=InstallmentResponseDTO,
    summary="Update installment",
    responses={
        200: {"description": "Installment updated successfully"},
        404: {"description": "Installment not found"},
        403: {"description": "Forbidden - Installment does not belong to user"},
        422: {"description": "Validation error"},
    },
)
def update_installment(
    installment_id: int,
    installment_data: UpdateInstallmentInputDTO,
    user_id: int = Query(..., description="User ID for authorization"),
    uow: IUnitOfWork = Depends(get_unit_of_work)
):
    """
    Update an installment's amount or manual statement assignment.

    Business rules:
    - Installment must belong to the authenticated user
    - Manual statement assignment must be to a statement of the same credit card
    - Amount changes update the purchase total automatically
    """
    try:
        use_case = UpdateInstallmentUseCase(uow)
        command = UpdateInstallmentCommand(
            installment_id=installment_id,
            user_id=user_id,
            amount=installment_data.amount,
            manually_assigned_statement_id=installment_data.manually_assigned_statement_id,
        )
        return use_case.execute(command)
    except InstallmentNotFoundError:
        raise HTTPException(status_code=404, detail="Installment not found")
    except PurchaseNotFoundError:
        raise HTTPException(status_code=403, detail="Installment does not belong to user")
    except MonthlyStatementNotFoundError:
        raise HTTPException(status_code=422, detail="Invalid statement assignment")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete(
    "/{installment_id}",
    summary="Delete installment",
    responses={
        204: {"description": "Installment deleted successfully"},
        404: {"description": "Installment not found"},
        403: {"description": "Forbidden - Installment does not belong to user"},
        422: {"description": "Business rule violation"},
    },
)
def delete_installment(
    installment_id: int,
    user_id: int = Query(..., description="User ID for authorization"),
    uow: IUnitOfWork = Depends(get_unit_of_work)
):
    """
    Delete an installment permanently.

    Business rules:
    - Installment must belong to the authenticated user
    - Cannot delete the last remaining installment of a purchase
    - Deletion is permanent and cannot be undone
    """
    try:
        use_case = DeleteInstallmentUseCase(uow)
        command = DeleteInstallmentCommand(
            installment_id=installment_id,
            user_id=user_id,
        )
        use_case.execute(command)
        return {"message": "Installment deleted successfully"}
    except InstallmentNotFoundError:
        raise HTTPException(status_code=404, detail="Installment not found")
    except PurchaseNotFoundError:
        raise HTTPException(status_code=403, detail="Installment does not belong to user")
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
