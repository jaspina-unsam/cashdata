"""Use case for listing monthly statements."""

from cashdata.application.dtos.monthly_statement_dto import MonthlyStatementResponseDTO
from cashdata.domain.repositories.icredit_card_repository import ICreditCardRepository
from cashdata.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)


class ListMonthlyStatementsUseCase:
    """Use case for listing monthly statements for a user."""

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
        self, user_id: int, include_future: bool = False
    ) -> list[MonthlyStatementResponseDTO]:
        """List all monthly statements for a user's credit cards.

        Args:
            user_id: The user's ID
            include_future: Whether to include statements with future payment dates

        Returns:
            List of monthly statements ordered by due_date descending
        """
        statements = self._statement_repository.find_all_by_user_id(
            user_id, include_future
        )

        # Build response DTOs with credit card names
        result = []
        for statement in statements:
            credit_card = self._credit_card_repository.find_by_id(
                statement.credit_card_id
            )
            if credit_card:
                result.append(
                    MonthlyStatementResponseDTO(
                        id=statement.id,
                        credit_card_id=statement.credit_card_id,
                        credit_card_name=credit_card.name,
                        start_date=statement.start_date,
                        closing_date=statement.closing_date,
                        due_date=statement.due_date,
                    )
                )

        return result
