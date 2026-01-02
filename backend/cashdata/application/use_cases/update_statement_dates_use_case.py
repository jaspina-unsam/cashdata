"""Use case for updating statement dates."""

from cashdata.application.dtos.monthly_statement_dto import (
    MonthlyStatementResponseDTO,
    UpdateStatementDatesInputDTO,
)
from cashdata.domain.entities.monthly_statement import MonthlyStatement
from cashdata.domain.repositories.icredit_card_repository import ICreditCardRepository
from cashdata.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)


class UpdateStatementDatesUseCase:
    """Use case for updating statement billing close and payment due dates."""

    def __init__(
        self,
        statement_repository: IMonthlyStatementRepository,
        credit_card_repository: ICreditCardRepository,
    ):
        """Initialize the use case.

        Args:
            statement_repository: Repository for monthly statements
            credit_card_repository: Repository for credit cards
        """
        self._statement_repository = statement_repository
        self._credit_card_repository = credit_card_repository

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
            billing_close_date=input_dto.billing_close_date,
            payment_due_date=input_dto.payment_due_date,
        )

        # Save
        saved_statement = self._statement_repository.save(updated_statement)

        return MonthlyStatementResponseDTO(
            id=saved_statement.id,
            credit_card_id=saved_statement.credit_card_id,
            credit_card_name=credit_card.name,
            billing_close_date=saved_statement.billing_close_date,
            payment_due_date=saved_statement.payment_due_date,
        )
