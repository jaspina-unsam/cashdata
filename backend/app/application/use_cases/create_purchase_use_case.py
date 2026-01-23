from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from app.application.exceptions.application_exceptions import (
    CreditCardNotFoundError,
    PaymentMethodInstallmentError,
    PaymentMethodNotFoundError,
    PaymentMethodOwnershipError,
)
from app.domain.entities.purchase import Purchase
from app.domain.value_objects.money import Money, Currency
from app.domain.value_objects.dual_money import DualMoney
from app.domain.value_objects.exchange_rate_type import ExchangeRateType
from app.domain.services.installment_generator import InstallmentGenerator
from app.domain.services.exchange_rate_finder import ExchangeRateFinder
from app.domain.services.inferred_exchange_rate_calculator import InferredExchangeRateCalculator
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.application.services.statement_factory import StatementFactory
from app.domain.services.payment_method_validator import PaymentMethodValidator
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.infrastructure.persistence.mappers.purchase_mapper import PurchaseMapper


@dataclass(frozen=True)
class CreatePurchaseCommand:
    """Command to create a new purchase"""

    user_id: int
    payment_method_id: int
    category_id: int
    purchase_date: date
    description: str
    total_amount: Decimal
    currency: str  # Currency as string from DTO
    installments_count: int
    # Dual-currency fields
    original_amount: Optional[Decimal] = None
    original_currency: Optional[str] = None
    rate_type: Optional[str] = None  # If None, auto-detect
    exchange_rate_id: Optional[int] = None  # Pre-selected exchange rate


@dataclass(frozen=True)
class CreatePurchaseResult:
    """Result of creating a purchase"""

    purchase_id: int
    payment_type: PaymentMethodType
    installments_count: int


class CreatePurchaseUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, command: CreatePurchaseCommand) -> CreatePurchaseResult:
        """
        Create a new purchase and its associated installments if applicable

        Args:
            command (CreatePurchaseCommand): The command containing purchase details

        Returns:
            CreatePurchaseResult: The result containing purchase ID and details

        Raises:
            PaymentMethodNotFoundError: If the payment method does not exist
            PaymentMethodOwnershipError: If the payment method does not belong to the user
            PaymentMethodInstallmentError: If the installments are invalid for the payment method
            CreditCardNotFoundError: If the credit card for the payment method is not found
        """
        with self.unit_of_work as uow:
            paymethod = uow.payment_methods.find_by_id(command.payment_method_id)
            if not paymethod:
                raise PaymentMethodNotFoundError(
                    f"Payment method with ID {command.payment_method_id} not found"
                )
            # For bank account payment methods, skip payment method ownership check
            # since bank account access validation will be performed later
            if paymethod.user_id != command.user_id and paymethod.type != PaymentMethodType.BANK_ACCOUNT:
                raise PaymentMethodOwnershipError(
                    f"Payment method {command.payment_method_id} does not belong to user {command.user_id}"
                )
            if not PaymentMethodValidator.validate_installments(
                paymethod, command.installments_count
            ):
                raise PaymentMethodInstallmentError(
                    "Only credit card payment methods can have multiple installments"
                )
            if paymethod.type == PaymentMethodType.CREDIT_CARD:
                credit_card = uow.credit_cards.find_by_payment_method_id(
                    command.payment_method_id
                )
                if not credit_card:
                    raise CreditCardNotFoundError(
                        f"Credit card for payment method ID {command.payment_method_id} not found"
                    )

            # - Si payment_method es bank_account, validar que user tenga acceso
            # - Llamar a `bank_account.has_access(user_id)`
            if paymethod.type == PaymentMethodType.BANK_ACCOUNT:
                bank_account = uow.bank_accounts.find_by_payment_method_id(
                    command.payment_method_id
                )
                if not bank_account.has_access(command.user_id):
                    raise PaymentMethodOwnershipError(
                        f"User {command.user_id} does not have access to bank account with payment method ID {command.payment_method_id}"
                    )

            # Validate category exists
            category = uow.categories.find_by_id(command.category_id)
            if not category:
                raise ValueError(f"Category with ID {command.category_id} not found")

            # Determine card currency for auto-conversion
            purchase_currency = Currency(command.currency)
            card_currency = None
            
            if paymethod.type == PaymentMethodType.CREDIT_CARD:
                if credit_card and credit_card.credit_limit:
                    card_currency = credit_card.credit_limit.currency

            # Build DualMoney for the purchase
            exchange_rate_entity = None
            
            # Auto-convert if purchase currency differs from card currency
            should_auto_convert = (
                card_currency is not None and 
                purchase_currency != card_currency and 
                command.original_amount is None
            )
            
            if should_auto_convert:
                # Purchase in foreign currency, auto-convert to card currency
                preferred_rate_type = ExchangeRateType.MEP  # Default to MEP
                if command.rate_type:
                    preferred_rate_type = ExchangeRateType(command.rate_type)
                
                # Try to find existing exchange rate
                rate_finder = ExchangeRateFinder(uow.exchange_rates)
                exchange_rate_entity = rate_finder.find_exchange_rate(
                    date=command.purchase_date,
                    from_currency=purchase_currency,
                    to_currency=card_currency,
                    preferred_type=preferred_rate_type,
                    user_id=command.user_id,
                )
                
                # Use found rate or fallback to 1500
                rate_value = exchange_rate_entity.rate if exchange_rate_entity else Decimal("1500.00")
                
                # Calculate converted amount (from purchase currency to card currency)
                converted_amount = command.total_amount * rate_value
                
                # Create DualMoney with card currency as primary, purchase currency as secondary
                total_amount = DualMoney(
                    primary_amount=converted_amount,
                    primary_currency=card_currency,
                    secondary_amount=command.total_amount,
                    secondary_currency=purchase_currency,
                    exchange_rate=rate_value,
                )
            elif command.original_amount is not None and command.original_currency is not None:
                # Dual-currency purchase
                original_curr = Currency(command.original_currency)
                total_curr = Currency(command.currency)
                
                # Try to use provided exchange_rate_id first
                if command.exchange_rate_id:
                    exchange_rate_entity = uow.exchange_rates.find_by_id(command.exchange_rate_id)
                    if not exchange_rate_entity:
                        raise ValueError(f"Exchange rate with ID {command.exchange_rate_id} not found")
                else:
                    # Determine exchange rate type to use
                    preferred_rate_type = None
                    if command.rate_type:
                        preferred_rate_type = ExchangeRateType(command.rate_type)
                    
                    # Try to find existing exchange rate
                    rate_finder = ExchangeRateFinder(uow.exchange_rates)
                    exchange_rate_entity = rate_finder.find_exchange_rate(
                        date=command.purchase_date,
                        from_currency=Currency.USD,  # Assuming always USD -> ARS
                        to_currency=Currency.ARS,
                        preferred_type=preferred_rate_type,
                        user_id=command.user_id,
                    )
                    
                    # If no exchange rate found and currencies are different, create inferred rate
                    if not exchange_rate_entity and original_curr != total_curr:
                        calculator = InferredExchangeRateCalculator()
                        exchange_rate_entity = calculator.create_inferred_rate_entity(
                            purchase_date=command.purchase_date,
                            original_amount=command.original_amount,
                            original_currency=original_curr,
                            converted_amount=command.total_amount,
                            converted_currency=total_curr,
                            user_id=command.user_id,
                        )
                        # Save the inferred exchange rate
                        exchange_rate_entity = uow.exchange_rates.save(exchange_rate_entity)
                
                total_amount = DualMoney(
                    primary_amount=command.total_amount,
                    primary_currency=total_curr,
                    secondary_amount=command.original_amount,
                    secondary_currency=original_curr,
                    exchange_rate=exchange_rate_entity.rate if exchange_rate_entity else None,
                )
            else:
                # Single-currency purchase
                total_amount = DualMoney(
                    primary_amount=command.total_amount,
                    primary_currency=Currency(command.currency),
                )

            # Create purchase entity
            purchase = Purchase(
                id=None,
                user_id=command.user_id,
                payment_method_id=command.payment_method_id,
                category_id=command.category_id,
                purchase_date=command.purchase_date,
                description=command.description,
                total_amount=total_amount,
                installments_count=command.installments_count,
            )

            # Save purchase
            saved_purchase = uow.purchases.save(purchase)
            
            # Update exchange_rate_id if applicable (must be done after save to have purchase.id)
            if exchange_rate_entity:
                from app.infrastructure.persistence.models.purchase_model import PurchaseModel
                purchase_model = uow.session.get(PurchaseModel, saved_purchase.id)
                if purchase_model:
                    purchase_model.exchange_rate_id = exchange_rate_entity.id
                    uow.session.flush()
                    
                    # Re-fetch purchase to get updated entity with exchange_rate_id
                    uow.session.refresh(purchase_model)
                    saved_purchase = PurchaseMapper.to_entity(purchase_model)

            if paymethod.type == PaymentMethodType.CREDIT_CARD:
                # Generate installments
                installments = InstallmentGenerator.generate_installments(
                    purchase_id=saved_purchase.id,
                    total_amount=saved_purchase.total_amount,
                    installments_count=saved_purchase.installments_count,
                    purchase_date=saved_purchase.purchase_date,
                    credit_card=credit_card,
                )

                # Save all installments
                saved_installments = uow.installments.save_all(installments)
                
                # Update exchange_rate_id for all installments if applicable
                if exchange_rate_entity:
                    from app.infrastructure.persistence.models.installment_model import InstallmentModel
                    # Get all saved installment IDs and update them
                    for installment in saved_installments:
                        if installment.id:  # Should have ID after save
                            installment_model = uow.session.get(InstallmentModel, installment.id)
                            if installment_model:
                                installment_model.exchange_rate_id = exchange_rate_entity.id
                    uow.session.flush()

                # Automatically create statements for all installment billing periods
                for installment in saved_installments:
                    StatementFactory.get_or_create_statement_for_period(
                        credit_card=credit_card,
                        billing_period=installment.billing_period,
                        statement_repository=uow.monthly_statements,
                    )

            # Commit transaction
            uow.commit()

            return CreatePurchaseResult(
                purchase_id=saved_purchase.id,
                payment_type=paymethod.type,
                installments_count=command.installments_count,
            )
