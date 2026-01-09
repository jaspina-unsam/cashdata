from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

from app.application.dtos.purchase_dto import UpdateInstallmentInputDTO, InstallmentResponseDTO
from app.application.exceptions.application_exceptions import (
    InstallmentNotFoundError,
    PurchaseNotFoundError,
    MonthlyStatementNotFoundError,
)
from app.application.mappers.purchase_dto_mapper import InstallmentDTOMapper
from app.domain.entities.installment import Installment
from app.domain.entities.purchase import Purchase
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.money import Money


@dataclass(frozen=True)
class UpdateInstallmentCommand:
    """Command to update an installment"""

    installment_id: int
    user_id: int
    amount: Optional[Decimal] = None
    manually_assigned_statement_id: Optional[int] = None


class UpdateInstallmentUseCase:
    """
    Use case to update an existing installment.

    Business Rules:
    - Installment must exist and belong to user's purchase
    - If manually_assigned_statement_id is provided, it must exist and belong to the same credit card
    - Amount changes require updating the purchase total_amount
    """

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, command: UpdateInstallmentCommand) -> InstallmentResponseDTO:
        """
        Updates an existing installment

        Args:
            command: Update command with installment data

        Returns:
            InstallmentResponseDTO: Updated installment data

        Raises:
            InstallmentNotFoundError: If installment doesn't exist
            PurchaseNotFoundError: If purchase doesn't belong to user
            MonthlyStatementNotFoundError: If manual statement assignment is invalid
        """
        with self._uow:
            # Find existing installment
            installment = self._uow.installments.find_by_id(command.installment_id)
            if not installment:
                raise InstallmentNotFoundError(f"Installment with ID {command.installment_id} not found")

            # Verify ownership through purchase
            purchase = self._uow.purchases.find_by_id(installment.purchase_id)
            if not purchase or purchase.user_id != command.user_id:
                raise PurchaseNotFoundError(f"Installment {command.installment_id} does not belong to user {command.user_id}")

            # Validate manual statement assignment if provided
            if command.manually_assigned_statement_id is not None:
                statement = self._uow.monthly_statements.find_by_id(command.manually_assigned_statement_id)
                if not statement:
                    raise MonthlyStatementNotFoundError(f"Monthly statement with ID {command.manually_assigned_statement_id} not found")
                if statement.credit_card_id != purchase.credit_card_id:
                    raise MonthlyStatementNotFoundError(f"Statement {command.manually_assigned_statement_id} does not belong to the same credit card")

            # Update installment
            updated_amount = command.amount if command.amount is not None else installment.amount.amount
            updated_installment = Installment(
                id=installment.id,
                purchase_id=installment.purchase_id,
                installment_number=installment.installment_number,
                total_installments=installment.total_installments,
                amount=Money(amount=updated_amount, currency=installment.amount.currency),
                billing_period=installment.billing_period,
                manually_assigned_statement_id=command.manually_assigned_statement_id,
            )

            # Save updated installment
            saved_installment = self._uow.installments.save(updated_installment)

            # If amount changed, update purchase total
            if command.amount is not None:
                all_installments = self._uow.installments.find_by_purchase_id(purchase.id)
                new_total = sum(inst.amount.amount for inst in all_installments)
                updated_purchase = Purchase(
                    id=purchase.id,
                    user_id=purchase.user_id,
                    credit_card_id=purchase.credit_card_id,
                    category_id=purchase.category_id,
                    purchase_date=purchase.purchase_date,
                    description=purchase.description,
                    total_amount=Money(amount=new_total, currency=purchase.total_amount.currency),
                    installments_count=purchase.installments_count,
                )
                self._uow.purchases.save(updated_purchase)

            self._uow.commit()

            return InstallmentDTOMapper.to_response_dto(saved_installment)