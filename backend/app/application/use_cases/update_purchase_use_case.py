from dataclasses import dataclass
from typing import Optional
from datetime import date
from decimal import Decimal

from app.application.dtos.purchase_dto import UpdatePurchaseInputDTO, PurchaseResponseDTO
from app.application.exceptions.application_exceptions import (
    PurchaseNotFoundError,
    PaymentMethodNotFoundError,
    PaymentMethodOwnershipError,
    CategoryNotFoundError,
)
from app.application.mappers.purchase_dto_mapper import PurchaseDTOMapper
from app.domain.entities.purchase import Purchase
from app.domain.entities.installment import Installment
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.money import Money


@dataclass(frozen=True)
class UpdatePurchaseCommand:
    """Command to update a purchase"""

    purchase_id: int
    user_id: int
    payment_method_id: Optional[int] = None
    category_id: Optional[int] = None
    purchase_date: Optional[date] = None
    description: Optional[str] = None
    total_amount: Optional[Decimal] = None


class UpdatePurchaseUseCase:
    """
    Use case to update an existing purchase.

    Note: Updating certain fields (like credit_card_id, purchase_date, total_amount)
    may require regenerating installments and statements, which is not implemented yet.
    Currently only updates basic purchase fields.
    """

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, command: UpdatePurchaseCommand) -> PurchaseResponseDTO:
        """
        Updates an existing purchase

        Args:
            command: Update command with purchase data

        Returns:
            PurchaseResponseDTO: Updated purchase data

        Raises:
            PurchaseNotFoundError: If purchase doesn't exist
            PaymentMethodNotFoundError: If payment method doesn't exist
            PaymentMethodOwnershipError: If payment method doesn't belong to user
            CategoryNotFoundError: If category doesn't exist
        """
        with self._uow:
            # Find existing purchase
            purchase = self._uow.purchases.find_by_id(command.purchase_id)
            if not purchase:
                raise PurchaseNotFoundError(f"Purchase with ID {command.purchase_id} not found")

            if purchase.user_id != command.user_id:
                raise PurchaseNotFoundError(f"Purchase with ID {command.purchase_id} not found")

            # Validate payment method if provided
            payment_method_id = command.payment_method_id if command.payment_method_id is not None else purchase.payment_method_id
            if command.payment_method_id is not None:
                payment_method = self._uow.payment_methods.find_by_id(command.payment_method_id)
                if not payment_method:
                    raise PaymentMethodNotFoundError(f"Payment method with ID {command.payment_method_id} not found")
                if payment_method.user_id != command.user_id:
                    raise PaymentMethodOwnershipError(f"Payment method {command.payment_method_id} does not belong to user {command.user_id}")

            # Validate category if provided
            category_id = command.category_id if command.category_id is not None else purchase.category_id
            if command.category_id is not None:
                category = self._uow.categories.find_by_id(command.category_id)
                if not category:
                    raise CategoryNotFoundError(f"Category with ID {command.category_id} not found")

            # For now, only update basic fields. Complex updates (payment_method, date) require
            # regenerating installments and statements, which is not implemented.
            # Amount updates are allowed for single-installment purchases only.
            if command.payment_method_id is not None or command.purchase_date is not None:
                raise ValueError("Updating payment_method_id or purchase_date is not yet supported")

            if command.total_amount is not None and purchase.installments_count > 1:
                raise ValueError("Updating total_amount is not supported for multi-installment purchases")

            # Handle amount update for single-installment purchases
            total_amount = command.total_amount if command.total_amount is not None else purchase.total_amount.amount
            total_amount_money = Money(amount=total_amount, currency=purchase.total_amount.currency) if command.total_amount is not None else purchase.total_amount
            if command.total_amount is not None and purchase.installments_count == 1:
                # Update the single installment amount
                installments = self._uow.installments.find_by_purchase_id(purchase.id)
                if len(installments) == 1:
                    installment = installments[0]
                    updated_installment = Installment(
                        id=installment.id,
                        purchase_id=installment.purchase_id,
                        installment_number=installment.installment_number,
                        total_installments=installment.total_installments,
                        amount=Money(amount=command.total_amount, currency=installment.amount.currency),
                        billing_period=installment.billing_period,
                        manually_assigned_statement_id=installment.manually_assigned_statement_id,
                    )
                    self._uow.installments.save(updated_installment)

            # Create updated purchase
            updated_purchase = Purchase(
                id=purchase.id,
                user_id=purchase.user_id,
                payment_method_id=payment_method_id,
                category_id=category_id,
                purchase_date=purchase.purchase_date,  # Not updating yet
                description=command.description if command.description is not None else purchase.description,
                total_amount=total_amount_money,
                installments_count=purchase.installments_count,
            )

            # Save updated purchase
            saved_purchase = self._uow.purchases.save(updated_purchase)

            self._uow.commit()

            return PurchaseDTOMapper.to_response_dto(saved_purchase)