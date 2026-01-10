from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.application.exceptions.application_exceptions import (
    CreditCardNotFoundError,
    PaymentMethodInstallmentError,
    PaymentMethodNotFoundError,
    PaymentMethodOwnershipError,
)
from app.domain.entities.purchase import Purchase
from app.domain.value_objects.money import Money, Currency
from app.domain.services.installment_generator import InstallmentGenerator
from app.domain.repositories import IUnitOfWork
from app.application.services.statement_factory import StatementFactory
from app.domain.services.payment_method_validator import PaymentMethodValidator
from app.domain.value_objects.payment_method_type import PaymentMethodType


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
            if paymethod.user_id != command.user_id:
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

            # Validate category exists
            category = uow.categories.find_by_id(command.category_id)
            if not category:
                raise ValueError(f"Category with ID {command.category_id} not found")

            # Create purchase entity
            purchase = Purchase(
                id=None,
                user_id=command.user_id,
                payment_method_id=command.payment_method_id,
                category_id=command.category_id,
                purchase_date=command.purchase_date,
                description=command.description,
                total_amount=Money(command.total_amount, Currency(command.currency)),
                installments_count=command.installments_count,
            )

            # Attach statement FK to purchase before saving
            purchase = Purchase(
                id=purchase.id,
                user_id=purchase.user_id,
                payment_method_id=purchase.payment_method_id,
                category_id=purchase.category_id,
                purchase_date=purchase.purchase_date,
                description=purchase.description,
                total_amount=purchase.total_amount,
                installments_count=purchase.installments_count,
            )

            # Save purchase
            saved_purchase = uow.purchases.save(purchase)

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
                uow.installments.save_all(installments)

                # Automatically create statements for all installment billing periods
                for installment in installments:
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
