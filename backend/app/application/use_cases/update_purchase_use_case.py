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
from app.domain.value_objects.money import Money, Currency
from app.domain.value_objects.dual_money import DualMoney
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.services.installment_generator import InstallmentGenerator
from app.domain.services.exchange_rate_finder import ExchangeRateFinder
from app.domain.value_objects.payment_method_type import PaymentMethodType


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
    # Dual-currency fields
    original_amount: Optional[Decimal] = None
    original_currency: Optional[str] = None
    exchange_rate_id: Optional[int] = None


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
        Updates an existing purchase and regenerates installments if amounts change

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

            # Get payment method for credit card check
            payment_method = self._uow.payment_methods.find_by_id(purchase.payment_method_id)
            if not payment_method:
                raise PaymentMethodNotFoundError(f"Payment method with ID {purchase.payment_method_id} not found")
            
            credit_card = None
            if payment_method.type == PaymentMethodType.CREDIT_CARD:
                credit_card = self._uow.credit_cards.find_by_payment_method_id(purchase.payment_method_id)

            # Validate category if provided
            category_id = command.category_id if command.category_id is not None else purchase.category_id
            if command.category_id is not None:
                category = self._uow.categories.find_by_id(command.category_id)
                if not category:
                    raise CategoryNotFoundError(f"Category with ID {command.category_id} not found")

            # Build updated DualMoney
            needs_regenerate = False
            total_amount = purchase.total_amount
            exchange_rate_entity = None
            
            # Check if dual-currency fields are being updated
            if (command.total_amount is not None or 
                command.original_amount is not None or 
                command.exchange_rate_id is not None):
                
                needs_regenerate = True
                
                # Start with current values
                primary_currency = purchase.total_amount.primary_currency
                primary_amount = command.total_amount if command.total_amount is not None else purchase.total_amount.primary_amount
                secondary_amount = None
                secondary_currency = None
                calculated_rate = None
                
                # If exchange_rate_id provided, use it
                if command.exchange_rate_id is not None:
                    exchange_rate_entity = self._uow.exchange_rates.find_by_id(command.exchange_rate_id)
                    if not exchange_rate_entity:
                        raise ValueError(f"Exchange rate with ID {command.exchange_rate_id} not found")
                    
                    calculated_rate = exchange_rate_entity.rate
                    
                    # Determine the secondary currency
                    if command.original_currency is not None:
                        # User explicitly specified the original currency
                        secondary_currency = Currency(command.original_currency)
                    else:
                        # Infer from exchange rate direction
                        if exchange_rate_entity.from_currency == primary_currency:
                            secondary_currency = exchange_rate_entity.to_currency
                        else:
                            secondary_currency = exchange_rate_entity.from_currency
                    
                    # If user provided original_amount, trust it; otherwise calculate it
                    if command.original_amount is not None:
                        secondary_amount = command.original_amount
                    else:
                        # Calculate secondary from primary using the rate
                        if exchange_rate_entity.from_currency == primary_currency:
                            secondary_amount = primary_amount * exchange_rate_entity.rate
                        else:
                            secondary_amount = primary_amount / exchange_rate_entity.rate
                            
                elif command.original_amount is not None:
                    # User provided custom amount without exchange_rate_id - create INFERRED rate
                    secondary_amount = command.original_amount
                    # Infer secondary currency based on primary currency
                    if primary_currency == Currency.USD:
                        secondary_currency = Currency.ARS
                    else:
                        secondary_currency = Currency.USD
                    calculated_rate = secondary_amount / primary_amount
                    
                    # Create an INFERRED exchange rate and save it
                    from app.domain.entities.exchange_rate import ExchangeRate
                    from app.domain.value_objects.exchange_rate_type import ExchangeRateType
                    from datetime import datetime
                    
                    inferred_rate = ExchangeRate(
                        id=None,
                        created_by_user_id=command.user_id,
                        from_currency=primary_currency,
                        to_currency=secondary_currency,
                        rate=calculated_rate,
                        date=command.purchase_date if command.purchase_date else purchase.purchase_date,
                        rate_type=ExchangeRateType.INFERRED,
                        created_at=datetime.now(),
                        source="INFERRED",
                    )
                    exchange_rate_entity = self._uow.exchange_rates.save(inferred_rate)
                
                # Build DualMoney
                if secondary_amount is not None and secondary_currency is not None and calculated_rate is not None:
                    total_amount = DualMoney(
                        primary_amount=primary_amount,
                        primary_currency=primary_currency,
                        secondary_amount=secondary_amount,
                        secondary_currency=secondary_currency,
                        exchange_rate=calculated_rate,
                    )
                else:
                    total_amount = DualMoney(
                        primary_amount=primary_amount,
                        primary_currency=primary_currency,
                    )

            # Create updated purchase
            updated_purchase = Purchase(
                id=purchase.id,
                user_id=purchase.user_id,
                payment_method_id=purchase.payment_method_id,
                category_id=category_id,
                purchase_date=purchase.purchase_date,
                description=command.description if command.description is not None else purchase.description,
                total_amount=total_amount,
                installments_count=purchase.installments_count,
            )

            # Save updated purchase
            saved_purchase = self._uow.purchases.save(updated_purchase)
            
            # Update exchange_rate_id if applicable
            from app.infrastructure.persistence.models.purchase_model import PurchaseModel
            purchase_model = self._uow.session.get(PurchaseModel, saved_purchase.id)
            if purchase_model:
                if exchange_rate_entity:
                    purchase_model.exchange_rate_id = exchange_rate_entity.id
                else:
                    purchase_model.exchange_rate_id = None
                self._uow.session.flush()

            # Regenerate installments if amounts changed and it's a credit card purchase
            if needs_regenerate and credit_card:
                # Delete existing installments
                existing_installments = self._uow.installments.find_by_purchase_id(purchase.id)
                for inst in existing_installments:
                    self._uow.installments.delete(inst.id)
                
                # Generate new installments
                new_installments = InstallmentGenerator.generate_installments(
                    purchase_id=saved_purchase.id,
                    total_amount=saved_purchase.total_amount,
                    installments_count=saved_purchase.installments_count,
                    purchase_date=saved_purchase.purchase_date,
                    credit_card=credit_card,
                )
                
                # Save new installments
                self._uow.installments.save_all(new_installments)

            self._uow.commit()

            # Get the updated purchase model to include exchange_rate_id in response
            from app.infrastructure.persistence.models.purchase_model import PurchaseModel
            updated_model = self._uow.session.get(PurchaseModel, saved_purchase.id)
            if not updated_model:
                raise PurchaseNotFoundError(f"Purchase with id {saved_purchase.id} not found after update")
            
            # Build response DTO from model to include exchange_rate_id
            return PurchaseResponseDTO(
                id=updated_model.id,
                user_id=updated_model.user_id,
                payment_method_id=updated_model.payment_method_id,
                category_id=updated_model.category_id,
                purchase_date=updated_model.purchase_date,
                description=updated_model.description,
                total_amount=Decimal(str(updated_model.total_amount)),
                currency=Currency(updated_model.total_currency),
                installments_count=updated_model.installments_count,
                original_amount=Decimal(str(updated_model.original_amount)) if updated_model.original_amount else None,
                original_currency=updated_model.original_currency,
                exchange_rate_id=updated_model.exchange_rate_id,
            )