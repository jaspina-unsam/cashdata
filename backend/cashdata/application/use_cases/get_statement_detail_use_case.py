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

        # Get purchases that were assigned to this statement (FK)
        purchases_by_fk = self._purchase_repository.find_by_monthly_statement_id(
            statement.id
        )

        # Also include purchases for this card that have installments in this billing period
        all_card_purchases = self._purchase_repository.find_by_credit_card_id(
            statement.credit_card_id
        )

        # Determine statement_period (YYYYMM)
        due_year = statement.due_date.year
        due_month = statement.due_date.month
        period_month = due_month - 1
        period_year = due_year
        if period_month < 1:
            period_month = 12
            period_year -= 1
        statement_period = f"{period_year:04d}{period_month:02d}"

        purchases_map: dict[int, Purchase] = {p.id: p for p in purchases_by_fk}

        for p in all_card_purchases:
            if p.id in purchases_map:
                continue
            installs = self._installment_repository.find_by_purchase_id(p.id)
            if any(inst.billing_period == statement_period for inst in installs):
                purchases_map[p.id] = p

        card_purchases = list(purchases_map.values())

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
                            float(installment.amount.amount),
                        )
                    )

        # Calculate total amount
        total_amount = sum(p.amount for p in statement_purchases)
        currency = (
            statement_purchases[0].currency
            if statement_purchases
            else (
                credit_card.credit_limit.currency if credit_card.credit_limit else "ARS"
            )
        )

        return StatementDetailDTO(
            id=statement.id,
            credit_card_id=statement.credit_card_id,
            credit_card_name=credit_card.name,
            start_date=statement.start_date,
            closing_date=statement.closing_date,
            due_date=statement.due_date,
            period_start_date=statement.start_date,
            period_end_date=statement.closing_date,
            purchases=statement_purchases,
            total_amount=total_amount,
            currency=currency,
        )

    def _create_purchase_dto(
        self,
        purchase: Purchase,
        installment_number: int | None,
        installment_amount: float | None = None,
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
        amount = (
            installment_amount
            if installment_amount is not None
            else float(purchase.total_amount.amount)
        )

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
