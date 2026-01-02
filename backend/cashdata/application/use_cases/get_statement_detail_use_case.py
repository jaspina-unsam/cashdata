"""Use case for getting monthly statement detail with purchases."""

from datetime import date

from cashdata.application.dtos.monthly_statement_dto import (
    PurchaseInStatementDTO,
    StatementDetailDTO,
)
from cashdata.domain.entities.purchase import Purchase
from cashdata.domain.repositories.icategory_repository import ICategoryRepository
from cashdata.domain.repositories.icredit_card_repository import ICreditCardRepository
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
    ):
        """Initialize the use case.

        Args:
            statement_repository: Repository for monthly statements
            credit_card_repository: Repository for credit cards
            purchase_repository: Repository for purchases
            category_repository: Repository for categories
        """
        self._statement_repository = statement_repository
        self._credit_card_repository = credit_card_repository
        self._purchase_repository = purchase_repository
        self._category_repository = category_repository

    def execute(self, statement_id: int, user_id: int) -> StatementDetailDTO | None:
        """Get statement detail with all purchases.

        Args:
            statement_id: The statement's ID
            user_id: The user's ID (for authorization)

        Returns:
            Statement detail with purchases, or None if not found or not authorized
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

        # Get all purchases for this user and card
        all_purchases = self._purchase_repository.find_by_user_id(user_id)
        card_purchases = [
            p for p in all_purchases if p.credit_card_id == statement.credit_card_id
        ]

        # Filter purchases that belong to this statement period
        statement_purchases = []
        for purchase in card_purchases:
            if statement.includes_purchase_date(
                purchase.purchase_date,
                previous_statement.billing_close_date if previous_statement else None,
            ):
                # Add full purchase or installments depending on installments_count
                if purchase.installments_count == 1:
                    # Single payment
                    statement_purchases.append(
                        self._create_purchase_dto(purchase, None)
                    )
                else:
                    # Multiple installments - include the one that falls in this period
                    installment_number = self._get_installment_number_for_period(
                        purchase, period_start, statement.billing_close_date
                    )
                    if installment_number:
                        statement_purchases.append(
                            self._create_purchase_dto(purchase, installment_number)
                        )

        return StatementDetailDTO(
            id=statement.id,
            credit_card_id=statement.credit_card_id,
            credit_card_name=credit_card.name,
            billing_close_date=statement.billing_close_date,
            payment_due_date=statement.payment_due_date,
            period_start_date=period_start,
            period_end_date=statement.billing_close_date,
            purchases=statement_purchases,
        )

    def _create_purchase_dto(
        self, purchase: Purchase, installment_number: int | None
    ) -> PurchaseInStatementDTO:
        """Create a purchase DTO with category name."""
        category = self._category_repository.find_by_id(purchase.category_id)
        category_name = category.name if category else "Unknown"

        return PurchaseInStatementDTO(
            id=purchase.id,
            description=purchase.description,
            purchase_date=purchase.purchase_date,
            amount=purchase.total_amount.amount,
            currency=purchase.total_amount.currency,
            installments=purchase.installments_count,
            installment_number=installment_number,
            category_name=category_name,
        )

    def _get_installment_number_for_period(
        self, purchase: Purchase, period_start: date, period_end: date
    ) -> int | None:
        """Determine which installment number falls in the given period.

        Installments are distributed consecutively starting from purchase month.
        For example: Purchase on Jan 15 with 3 installments:
        - Installment 1: Jan statement (closes in Jan)
        - Installment 2: Feb statement (closes in Feb)
        - Installment 3: Mar statement (closes in Mar)

        Args:
            purchase: The purchase with multiple installments
            period_start: Statement period start date
            period_end: Statement period end date (billing close date)

        Returns:
            The installment number (1-N) if one falls in this period, None otherwise
        """
        # Calculate which month the purchase was made
        purchase_year = purchase.purchase_date.year
        purchase_month = purchase.purchase_date.month

        # Calculate which month this period ends
        period_year = period_end.year
        period_month = period_end.month

        # Calculate month difference
        month_diff = (period_year - purchase_year) * 12 + (
            period_month - purchase_month
        )

        # Installment number is month_diff + 1 (first installment is month 0)
        installment_number = month_diff + 1

        # Check if this installment exists (must be between 1 and installments_count)
        if 1 <= installment_number <= purchase.installments_count:
            return installment_number

        return None
