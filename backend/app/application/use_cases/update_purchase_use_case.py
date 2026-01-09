from dataclasses import dataclass
from typing import Optional
from datetime import date
from decimal import Decimal

from app.application.dtos.purchase_dto import UpdatePurchaseInputDTO, PurchaseResponseDTO
from app.application.exceptions.application_exceptions import (
    PurchaseNotFoundError,
    CreditCardNotFoundError,
    CreditCardOwnerMismatchError,
    CategoryNotFoundError,
)
from app.application.mappers.purchase_dto_mapper import PurchaseDTOMapper
from app.domain.entities.purchase import Purchase
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.money import Money


@dataclass(frozen=True)
class UpdatePurchaseCommand:
    """Command to update a purchase"""

    purchase_id: int
    user_id: int
    credit_card_id: Optional[int] = None
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
            CreditCardNotFoundError: If credit card doesn't exist
            CreditCardOwnerMismatchError: If credit card doesn't belong to user
            CategoryNotFoundError: If category doesn't exist
        """
        with self._uow:
            # Find existing purchase
            purchase = self._uow.purchases.find_by_id(command.purchase_id)
            if not purchase:
                raise PurchaseNotFoundError(f"Purchase with ID {command.purchase_id} not found")

            if purchase.user_id != command.user_id:
                raise PurchaseNotFoundError(f"Purchase {command.purchase_id} does not belong to user {command.user_id}")

            # Validate credit card if provided
            credit_card_id = command.credit_card_id if command.credit_card_id is not None else purchase.credit_card_id
            if command.credit_card_id is not None:
                credit_card = self._uow.credit_cards.find_by_id(command.credit_card_id)
                if not credit_card:
                    raise CreditCardNotFoundError(f"Credit card with ID {command.credit_card_id} not found")
                if credit_card.user_id != command.user_id:
                    raise CreditCardOwnerMismatchError(f"Credit card {command.credit_card_id} does not belong to user {command.user_id}")

            # Validate category if provided
            category_id = command.category_id if command.category_id is not None else purchase.category_id
            if command.category_id is not None:
                category = self._uow.categories.find_by_id(command.category_id)
                if not category:
                    raise CategoryNotFoundError(f"Category with ID {command.category_id} not found")

            # For now, only update basic fields. Complex updates (credit_card, date, amount) require
            # regenerating installments and statements, which is not implemented.
            if command.credit_card_id is not None or command.purchase_date is not None or command.total_amount is not None:
                raise ValueError("Updating credit_card_id, purchase_date, or total_amount is not yet supported")

            # Create updated purchase
            updated_purchase = Purchase(
                id=purchase.id,
                user_id=purchase.user_id,
                credit_card_id=credit_card_id,
                category_id=category_id,
                purchase_date=purchase.purchase_date,  # Not updating yet
                description=command.description if command.description is not None else purchase.description,
                total_amount=purchase.total_amount,  # Not updating yet
                installments_count=purchase.installments_count,
            )

            # Save updated purchase
            saved_purchase = self._uow.purchases.save(updated_purchase)

            self._uow.commit()

            return PurchaseDTOMapper.to_response_dto(saved_purchase)