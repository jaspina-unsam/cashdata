"""Use case for getting monthly statement detail with purchases."""

from app.application.dtos.monthly_statement_dto import (
    PurchaseInStatementDTO,
    StatementDetailDTO,
)
from app.domain.entities.purchase import Purchase
from app.domain.repositories.icategory_repository import ICategoryRepository
from app.domain.repositories.icredit_card_repository import ICreditCardRepository
from app.domain.repositories.iinstallment_repository import IInstallmentRepository
from app.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)
from app.domain.repositories.ipurchase_repository import IPurchaseRepository


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
        self._statement_repo = statement_repository
        self._credit_card_repo = credit_card_repository
        self._purchase_repo = purchase_repository
        self._category_repo = category_repository
        self._installment_repo = installment_repository

    def execute(self, statement_id: int, user_id: int) -> StatementDetailDTO | None:
        """Get statement detail with all installments that fall in this period.

        Args:
            statement_id: The statement's ID
            user_id: The user's ID (for authorization)

        Returns:
            Statement detail with purchases/installments, or None if not found or not authorized
        """
        statement = self._statement_repo.find_by_id(statement_id)
        if not statement:
            return None

        # Get credit card to verify ownership
        credit_card = self._credit_card_repo.find_by_id(statement.credit_card_id)
        if not credit_card or credit_card.user_id != user_id:
            return None

        # Get the card's currency for proper total calculation
        card_currency = credit_card.credit_limit.currency

        # Get purchases that were made with this credit card's payment method
        all_purchases = self._purchase_repo.find_by_payment_method_id(credit_card.payment_method_id)

        # Get period identifier
        period = statement.get_period_identifier()

        # Filter purchases with installments in this period or manually assigned to this statement
        statement_purchases = []
        for purchase in all_purchases:
            installments = self._installment_repo.find_by_purchase_id(purchase.id)

            for installment in installments:
                # Include installment if:
                # 1. It's manually assigned to this statement, OR
                # 2. It's automatically assigned to this statement (billing_period matches) AND not manually assigned elsewhere
                should_include = (
                    installment.manually_assigned_statement_id == statement_id or
                    (installment.billing_period == period and installment.manually_assigned_statement_id is None)
                )
                if should_include:
                    statement_purchases.append(
                        self._create_purchase_dto(
                            purchase,
                            installment,
                            card_currency,
                        )
                    )

        # Calculate total in card's currency (summing primary amounts which are in card currency)
        # The primary_amount in each purchase is already in the card's currency (ARS for ARS cards)
        # For purchases made in USD, the primary_amount is the ARS equivalent
        total = sum([p.amount for p in statement_purchases])

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
            total_amount=total,
            currency=card_currency,
        )

    def _create_purchase_dto(
        self,
        purchase: Purchase,
        installment: "Installment",
        card_currency: str,
    ) -> PurchaseInStatementDTO:
        """Create a purchase DTO with category name.

        Args:
            purchase: The purchase entity
            installment: The installment entity
            card_currency: The currency of the credit card (for proper conversion)
        """
        from app.domain.entities.installment import Installment
        from app.domain.value_objects.money import Currency
        
        category = self._category_repo.find_by_id(purchase.category_id)
        category_name = category.name if category else "Unknown"

        # Get installment amount in card currency
        installment_amount = installment.amount
        
        # Determine primary and secondary amounts based on card currency
        # We ALWAYS want to show the amount in the card's currency
        card_currency_enum = Currency[card_currency]
        
        if installment_amount.is_dual_currency():
            # For dual currency, we need to figure out which is in card currency
            if installment_amount.primary_currency == card_currency_enum:
                # Primary is already in card currency - perfect!
                amount = float(installment_amount.primary_amount)
                currency = installment_amount.primary_currency.value
                original_amount = float(installment_amount.secondary_amount)
                original_currency = installment_amount.secondary_currency.value
            elif installment_amount.secondary_currency == card_currency_enum:
                # Secondary is in card currency - swap them for display
                amount = float(installment_amount.secondary_amount)
                currency = installment_amount.secondary_currency.value
                original_amount = float(installment_amount.primary_amount)
                original_currency = installment_amount.primary_currency.value
            else:
                # Neither matches card currency (shouldn't happen in bimonetary setup)
                # Fall back to primary
                amount = float(installment_amount.primary_amount)
                currency = installment_amount.primary_currency.value
                original_amount = float(installment_amount.secondary_amount)
                original_currency = installment_amount.secondary_currency.value
        else:
            # Single currency installment
            amount = float(installment_amount.primary_amount)
            currency = installment_amount.primary_currency.value
            original_amount = None
            original_currency = None

        return PurchaseInStatementDTO(
            id=purchase.id,
            description=purchase.description,
            purchase_date=purchase.purchase_date,
            amount=amount,
            currency=currency,
            installments=purchase.installments_count,
            installment_number=installment.installment_number,
            category_name=category_name,
            original_amount=original_amount,
            original_currency=original_currency,
            exchange_rate_id=None,
        )
