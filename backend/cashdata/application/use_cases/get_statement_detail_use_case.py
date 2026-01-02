"""Use case for getting monthly statement detail with purchases."""

from datetime import date

from cashdata.application.dtos.monthly_statement_dto import (
    PurchaseInStatementDTO,
    StatementDetailDTO,
)
from cashdata.domain.entities.purchase import Purchase
from cashdata.domain.repositories.icategory_repository import ICategoryRepository
from cashdata.domain.repositories.icredit_card_repository import ICreditCardRepository
from cashdata.domain.repositories.iinstallment_repository import IInstallmentRepository
from cashdata.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)
from cashdata.domain.repositories.ipurchase_repository import IPurchaseRepository


class GetStatementDetailUseCase:
    """Use case for getting statement detail with all purchases."""

    def __init__(
        self,
        statement_repository: IMonthlyStatementRepository,
        credit_card_repository: ICreditCardRepository,
        purchase_repository: IPurchaseRepository,
        category_repository: ICategoryRepository,
        installment_repository: IInstallmentRepository,
    ):
        """Initialize the use case.

        Args:
            statement_repository: Repository for monthly statements
            credit_card_repository: Repository for credit cards
            purchase_repository: Repository for purchases
            category_repository: Repository for categories
            installment_repository: Repository for installments
        """
        self._statement_repository = statement_repository
        self._credit_card_repository = credit_card_repository
        self._purchase_repository = purchase_repository
        self._category_repository = category_repository
        self._installment_repository = installment_repository

    def execute(self, statement_id: int, user_id: int) -> StatementDetailDTO | None:
        """Get statement detail with all installments that fall in this period.

        Args:
            statement_id: The statement's ID
            user_id: The user's ID (for authorization)

        Returns:
            Statement detail with purchases/installments, or None if not found or not authorized
        """
        statement = self._statement_repository.find_by_id(statement_id)
        if not statement:
            return None

        # Get credit card to verify ownership
        credit_card = self._credit_card_repository.find_by_id(statement.credit_card_id)
        if not credit_card or credit_card.user_id != user_id:
            return None

        # Get previous statement to calculate period start
        previous_statement = self._statement_repository.get_previous_statement(
            statement.credit_card_id, statement.billing_close_date
        )

        period_start = statement.get_period_start_date(
            previous_statement.billing_close_date if previous_statement else None
        )

        # Get all installments for this card that belong to this billing period
        # We query all user purchases to get the ones for this card
        all_purchases = self._purchase_repository.find_by_user_id(user_id)
        card_purchases = [
            p for p in all_purchases if p.credit_card_id == statement.credit_card_id
        ]

        # Calculate the billing period for this statement (format: YYYYMM)
        statement_period = statement.billing_close_date.strftime("%Y%m")

        # Now get installments for each purchase and filter by billing_period
        statement_purchases = []
        for purchase in card_purchases:
            # Get installments for this purchase
            installments = self._installment_repository.find_by_purchase_id(purchase.id)
            
            # Filter installments whose billing_period matches this statement's period
            for installment in installments:
                if installment.billing_period == statement_period:
                    statement_purchases.append(
                        self._create_purchase_dto(
                            purchase, 
                            installment.installment_number,
                            installment.amount.amount
                        )
                    )

        # Calculate total amount
        total_amount = sum(p.amount for p in statement_purchases)
        currency = statement_purchases[0].currency if statement_purchases else credit_card.credit_limit.currency if credit_card.credit_limit else "ARS"

        return StatementDetailDTO(
            id=statement.id,
            credit_card_id=statement.credit_card_id,
            credit_card_name=credit_card.name,
            billing_close_date=statement.billing_close_date,
            payment_due_date=statement.payment_due_date,
            period_start_date=period_start,
            period_end_date=statement.billing_close_date,
            purchases=statement_purchases,
            total_amount=total_amount,
            currency=currency,
        )

    def _create_purchase_dto(
        self, purchase: Purchase, installment_number: int | None, installment_amount: float | None = None
    ) -> PurchaseInStatementDTO:
        """Create a purchase DTO with category name.
        
        Args:
            purchase: The purchase entity
            installment_number: The installment number if this is an installment
            installment_amount: The installment amount (if different from total)
        """
        category = self._category_repository.find_by_id(purchase.category_id)
        category_name = category.name if category else "Unknown"

        # Use installment amount if provided, otherwise use total amount
        amount = installment_amount if installment_amount is not None else purchase.total_amount.amount

        return PurchaseInStatementDTO(
            id=purchase.id,
            description=purchase.description,
            purchase_date=purchase.purchase_date,
            amount=amount,
            currency=purchase.total_amount.currency,
            installments=purchase.installments_count,
            installment_number=installment_number,
            category_name=category_name,
        )
