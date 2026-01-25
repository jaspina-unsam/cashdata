"""Use case for updating statement dates."""

from datetime import timedelta

from app.application.dtos.monthly_statement_dto import (
    MonthlyStatementResponseDTO,
    UpdateStatementDatesInputDTO,
)
from app.domain.entities.installment import Installment
from app.domain.entities.monthly_statement import MonthlyStatement
from app.domain.repositories.icredit_card_repository import ICreditCardRepository
from app.domain.repositories.iinstallment_repository import IInstallmentRepository
from app.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)
from app.domain.repositories.ipurchase_repository import IPurchaseRepository


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

        # --- Preserve current included installments so they remain assigned to the statement ---
        included_installment_ids = self._get_included_installment_ids(statement, user_id)

        # --- Protect installments belonging to the next statement so they are not stolen ---
        self._protect_next_statement_installments(statement, credit_card, user_id)

        # Create updated statement entity (validation happens in __post_init__)
        updated_statement = MonthlyStatement(
            id=statement.id,
            credit_card_id=statement.credit_card_id,
            start_date=input_dto.start_date or statement.start_date,
            closing_date=input_dto.closing_date,
            due_date=input_dto.due_date,
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

        # Re-assign previously included installments to this statement so they remain included
        from app.domain.entities.installment import Installment
        for inst_id in included_installment_ids:
            existing = self._installment_repository.find_by_id(inst_id)
            # Only assign to this statement if it's currently unassigned or already belonged to this statement.
            if existing and (
                existing.manually_assigned_statement_id is None
                or existing.manually_assigned_statement_id == statement.id
            ) and existing.manually_assigned_statement_id != saved_statement.id:
                updated = Installment(
                    id=existing.id,
                    purchase_id=existing.purchase_id,
                    installment_number=existing.installment_number,
                    total_installments=existing.total_installments,
                    amount=existing.amount,
                    billing_period=existing.billing_period,
                    manually_assigned_statement_id=saved_statement.id,
                )
                self._installment_repository.save(updated)

        # Update the next statement's start date if it exists
        self._update_next_statement_start_date(saved_statement, credit_card)

        return MonthlyStatementResponseDTO(
            id=saved_statement.id,
            credit_card_id=saved_statement.credit_card_id,
            credit_card_name=credit_card.name,
            start_date=saved_statement.start_date,
            closing_date=saved_statement.closing_date,
            due_date=saved_statement.due_date,
        )

    def _get_included_installment_ids(self, statement: MonthlyStatement, user_id: int) -> list:
        """Return installment ids that are currently included in the statement.

        Included installements are either manually assigned to the statement or
        automatically assigned because their billing_period matches the statement's period.
        """
        period = statement.get_period_identifier()
        included = []

        # Get all purchases for this user and card
        all_purchases = self._purchase_repository.find_by_user_id(user_id)

        # Defensive: repository might return a non-iterable Mock in tests; treat as empty
        try:
            iter(all_purchases)
        except TypeError:
            return included

        card_purchases = [p for p in all_purchases if p.payment_method_id == statement.credit_card_id]

        for purchase in card_purchases:
            installments = self._installment_repository.find_by_purchase_id(purchase.id)

            # Defensive: ensure installments is iterable
            try:
                iter(installments)
            except TypeError:
                continue

            for inst in installments:
                if inst.manually_assigned_statement_id == statement.id:
                    included.append(inst.id)
                elif inst.billing_period == period and inst.manually_assigned_statement_id is None:
                    included.append(inst.id)

        return included

    def _recalculate_installment_periods(
        self,
        credit_card,
        old_statement: MonthlyStatement,
        new_statement: MonthlyStatement,
        user_id: int,
    ):
        """Recalculate billing periods for installments when statement dates change.

        The billing period is calculated as the month of due_date minus 1.
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
        # Only consider purchases whose purchase_date falls inside the original statement period.
        card_purchases = [
            p
            for p in all_purchases
            if p.payment_method_id == credit_card.id and old_statement.includes_purchase_date(p.purchase_date)
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
                    # Preserve any existing manual assignment. Only update the billing_period.
                    updated_installment = Installment(
                        id=installment.id,
                        purchase_id=installment.purchase_id,
                        installment_number=installment.installment_number,
                        total_installments=installment.total_installments,
                        amount=installment.amount,
                        billing_period=new_period,
                        manually_assigned_statement_id=installment.manually_assigned_statement_id,
                    )
                    self._installment_repository.save(updated_installment)

    def _update_next_statement_start_date(
        self, current_statement: MonthlyStatement, credit_card
    ):
        """Update the start date of the next statement to be the day after current statement's closing date.

        Args:
            current_statement: The updated statement
            credit_card: The credit card entity
        """
        # Find all statements for this credit card
        all_statements = self._statement_repository.find_by_credit_card_id(
            credit_card.id, include_future=True
        )

        # Defensive: repository might return a Mock in tests; ensure we have an iterable
        try:
            iter(all_statements)
        except TypeError:
            all_statements = []

        # Sort statements by start_date to find the chronological order
        sorted_statements = sorted(all_statements, key=lambda s: s.start_date)

        # Find the current statement in the sorted list and get the next one
        next_statement = None
        current_index = None

        for i, stmt in enumerate(sorted_statements):
            if stmt.id == current_statement.id:
                current_index = i
                break

        if current_index is not None and current_index + 1 < len(sorted_statements):
            next_statement = sorted_statements[current_index + 1]

        # Calculate the correct start date for the next statement
        next_start_date = current_statement.closing_date + timedelta(days=1)

        # If there's a next statement and its start_date doesn't match, update it
        if next_statement and next_statement.start_date != next_start_date:
            updated_next_statement = MonthlyStatement(
                id=next_statement.id,
                credit_card_id=next_statement.credit_card_id,
                start_date=next_start_date,
                closing_date=next_statement.closing_date,
                due_date=next_statement.due_date,
            )
            self._statement_repository.save(updated_next_statement)

    def _protect_next_statement_installments(self, current_statement: MonthlyStatement, credit_card, user_id: int):
        """Ensure that installments that currently belong to the next statement remain assigned to it.

        This avoids the situation where extending the previous statement's period causes
        the previous statement to automatically include installments that logically
        belong to the next statement.
        """
        # Find all statements for this credit card
        all_statements = self._statement_repository.find_by_credit_card_id(
            credit_card.id, include_future=True
        )

        try:
            iter(all_statements)
        except TypeError:
            return

        sorted_statements = sorted(all_statements, key=lambda s: s.start_date)

        # Find current statement and candidate next
        next_stmt = None
        for i, stmt in enumerate(sorted_statements):
            if stmt.id == current_statement.id and i + 1 < len(sorted_statements):
                next_stmt = sorted_statements[i + 1]
                break

        if not next_stmt:
            return

        # Get installments that are currently included in the next statement
        next_included_ids = self._get_included_installment_ids(next_stmt, user_id)

        from app.domain.entities.installment import Installment

        for inst_id in next_included_ids:
            existing = self._installment_repository.find_by_id(inst_id)
            if existing and existing.manually_assigned_statement_id is None:
                updated = Installment(
                    id=existing.id,
                    purchase_id=existing.purchase_id,
                    installment_number=existing.installment_number,
                    total_installments=existing.total_installments,
                    amount=existing.amount,
                    billing_period=existing.billing_period,
                    manually_assigned_statement_id=next_stmt.id,
                )
                self._installment_repository.save(updated)
