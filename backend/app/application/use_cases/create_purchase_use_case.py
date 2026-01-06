from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.domain.entities.purchase import Purchase
from app.domain.value_objects.money import Money, Currency
from app.domain.services.installment_generator import InstallmentGenerator
from app.domain.repositories import IUnitOfWork
from app.application.services.statement_finder import StatementFinder


@dataclass(frozen=True)
class CreatePurchaseCommand:
    """Command to create a new purchase"""

    user_id: int
    credit_card_id: int
    category_id: int
    purchase_date: date
    description: str
    total_amount: Decimal
    currency: Currency
    installments_count: int


@dataclass(frozen=True)
class CreatePurchaseResult:
    """Result of creating a purchase"""

    purchase_id: int
    installments_count: int


class CreatePurchaseUseCase:
    """
    Use case to create a purchase and its installments.

    This use case:
    1. Creates a Purchase entity
    2. Generates installments using InstallmentGenerator
    3. Persists everything using UnitOfWork
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, command: CreatePurchaseCommand) -> CreatePurchaseResult:
        """
        Execute the use case to create a purchase with its installments.

        Args:
            command: The command containing purchase data

        Returns:
            CreatePurchaseResult with the created purchase ID and installment count

        Raises:
            ValueError: If credit card doesn't exist or doesn't belong to user
            ValueError: If category doesn't exist
        """
        with self.unit_of_work as uow:
            # Validate credit card exists and belongs to user
            credit_card = uow.credit_cards.find_by_id(command.credit_card_id)
            if not credit_card:
                raise ValueError(
                    f"Credit card with ID {command.credit_card_id} not found"
                )
            if credit_card.user_id != command.user_id:
                raise ValueError(
                    f"Credit card {command.credit_card_id} does not belong to user {command.user_id}"
                )

            # Validate category exists
            category = uow.categories.find_by_id(command.category_id)
            if not category:
                raise ValueError(f"Category with ID {command.category_id} not found")

            # Create purchase entity
            purchase = Purchase(
                id=None,
                user_id=command.user_id,
                credit_card_id=command.credit_card_id,
                category_id=command.category_id,
                purchase_date=command.purchase_date,
                description=command.description,
                total_amount=Money(command.total_amount, command.currency),
                installments_count=command.installments_count,
            )

            # Attach statement FK to purchase before saving
            purchase = Purchase(
                id=purchase.id,
                user_id=purchase.user_id,
                credit_card_id=purchase.credit_card_id,
                category_id=purchase.category_id,
                purchase_date=purchase.purchase_date,
                description=purchase.description,
                total_amount=purchase.total_amount,
                installments_count=purchase.installments_count,
            )

            # Save purchase
            saved_purchase = uow.purchases.save(purchase)

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
                StatementFinder.get_or_create_statement_for_period(
                    credit_card=credit_card,
                    billing_period=installment.billing_period,
                    statement_repository=uow.monthly_statements,
                )

            # Commit transaction
            uow.commit()

            return CreatePurchaseResult(
                purchase_id=saved_purchase.id, installments_count=len(installments)
            )
