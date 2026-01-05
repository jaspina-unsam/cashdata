"""Use case for updating statement dates."""

from cashdata.application.dtos.monthly_statement_dto import (
    MonthlyStatementResponseDTO,
    UpdateStatementDatesInputDTO,
)
from cashdata.domain.entities.installment import Installment
from cashdata.domain.entities.monthly_statement import MonthlyStatement
from cashdata.domain.repositories.icredit_card_repository import ICreditCardRepository
from cashdata.domain.repositories.iinstallment_repository import IInstallmentRepository
from cashdata.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)
from cashdata.domain.repositories.ipurchase_repository import IPurchaseRepository


class UpdateStatementDatesUseCase:
    """Use case for updating statement billing close and payment due dates."""

    def __init__(
        self,
        statement_repository: IMonthlyStatementRepository,
        credit_card_repository: ICreditCardRepository,
        purchase_repository: IPurchaseRepository,
        installment_repository: IInstallmentRepository,
    ):
        """Initialize the use case.

        Args:
            statement_repository: Repository for monthly statements
            credit_card_repository: Repository for credit cards
            purchase_repository: Repository for purchases
            installment_repository: Repository for installments
        """
        self._statement_repository = statement_repository
        self._credit_card_repository = credit_card_repository
        self._purchase_repository = purchase_repository
        self._installment_repository = installment_repository

    def execute(
        self, statement_id: int, user_id: int, input_dto: UpdateStatementDatesInputDTO
    ) -> MonthlyStatementResponseDTO | None:
        """Update statement dates.

        When dates are updated, the period changes which may affect which purchases
        belong to this statement. The frontend should refresh the statement detail
        after this operation to show the updated purchase list.

        Args:
            statement_id: The statement's ID
            user_id: The user's ID (for authorization)
            input_dto: The new dates

        Returns:
            Updated statement DTO, or None if not found/not authorized

        Raises:
            ValueError: If dates are invalid (close_date > due_date)
        """
        # Find and authorize
        statement = self._statement_repository.find_by_id(statement_id)
        if not statement:
            return None

        credit_card = self._credit_card_repository.find_by_id(statement.credit_card_id)
        if not credit_card or credit_card.user_id != user_id:
            return None

        # Create updated statement entity (validation happens in __post_init__)
        updated_statement = MonthlyStatement(
            id=statement.id,
            credit_card_id=statement.credit_card_id,
            closing_date=input_dto.billing_close_date,
            due_date=input_dto.payment_due_date,
        )

        # Save statement
        saved_statement = self._statement_repository.save(updated_statement)

        # Recalculate billing_period for all affected installments
        # Get the new period (YYYYMM format) - month of due_date minus 1
        due_year = saved_statement.due_date.year
        due_month = saved_statement.due_date.month
        period_month = due_month - 1
        period_year = due_year
        if period_month < 1:
            period_month = 12
            period_year -= 1
        new_period = f"{period_year:04d}{period_month:02d}"

        # Calculate old period
        old_due_year = statement.due_date.year
        old_due_month = statement.due_date.month
        old_period_month = old_due_month - 1
        old_period_year = old_due_year
        if old_period_month < 1:
            old_period_month = 12
            old_period_year -= 1
        old_period = f"{old_period_year:04d}{old_period_month:02d}"

        # If period changed, we need to update installments
        if new_period != old_period:
            self._recalculate_installment_periods(
                credit_card, statement, saved_statement, user_id
            )

        return MonthlyStatementResponseDTO(
            id=saved_statement.id,
            credit_card_id=saved_statement.credit_card_id,
            credit_card_name=credit_card.name,
            billing_close_date=saved_statement.closing_date,
            payment_due_date=saved_statement.due_date,
        )

    def _recalculate_installment_periods(
        self,
        credit_card,
        old_statement: MonthlyStatement,
        new_statement: MonthlyStatement,
        user_id: int,
    ):
        """Recalculate billing periods for installments when statement dates change.

        The billing period is calculated as the month of payment_due_date minus 1.
        This represents the month when the charges were made, not when the statement closes.

        Args:
            credit_card: The credit card entity
            old_statement: The original statement before update
            new_statement: The updated statement with new dates
            user_id: The user's ID for filtering purchases
        """
        # Calculate old and new periods using due_date - 1 logic
        old_due_year = old_statement.due_date.year
        old_due_month = old_statement.due_date.month
        old_period_month = old_due_month - 1
        old_period_year = old_due_year
        if old_period_month < 1:
            old_period_month = 12
            old_period_year -= 1
        old_period = f"{old_period_year:04d}{old_period_month:02d}"

        new_due_year = new_statement.due_date.year
        new_due_month = new_statement.due_date.month
        new_period_month = new_due_month - 1
        new_period_year = new_due_year
        if new_period_month < 1:
            new_period_month = 12
            new_period_year -= 1
        new_period = f"{new_period_year:04d}{new_period_month:02d}"

        # Get all purchases for this user and card
        all_purchases = self._purchase_repository.find_by_user_id(user_id)
        card_purchases = [
            p for p in all_purchases if p.credit_card_id == credit_card.id
        ]

        # For each purchase, update installments that were in the old period
        for purchase in card_purchases:
            installments = self._installment_repository.find_by_purchase_id(purchase.id)

            for installment in installments:
                # If this installment was in the old period, update it to new period
                if installment.billing_period == old_period:
                    # Calculate the correct due date for this installment in the new period
                    # The installment keeps its relative position (installment_number)
                    # but gets updated to the new period
                    updated_installment = Installment(
                        id=installment.id,
                        purchase_id=installment.purchase_id,
                        installment_number=installment.installment_number,
                        total_installments=installment.total_installments,
                        amount=installment.amount,
                        billing_period=new_period,
                        due_date=installment.due_date,
                    )
                    self._installment_repository.save(updated_installment)
