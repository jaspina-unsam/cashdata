"""Use case for creating a monthly statement."""

from cashdata.application.dtos.monthly_statement_dto import (
    CreateStatementInputDTO,
    MonthlyStatementResponseDTO,
)
from cashdata.domain.entities.monthly_statement import MonthlyStatement
from cashdata.domain.repositories.icredit_card_repository import ICreditCardRepository
from cashdata.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)


class CreateStatementUseCase:
    """Use case for creating a new monthly statement."""

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
        self, user_id: int, input_dto: CreateStatementInputDTO
    ) -> MonthlyStatementResponseDTO:
        """Create a new monthly statement.

        Args:
            user_id: The user's ID (for authorization)
            input_dto: The statement data

        Returns:
            Created statement DTO

        Raises:
            ValueError: If credit card doesn't exist, doesn't belong to user,
                       or dates are invalid (close_date > due_date)
        """
        # Verify credit card exists and belongs to user
        credit_card = self._credit_card_repository.find_by_id(input_dto.credit_card_id)
        if not credit_card:
            raise ValueError(
                f"Credit card with id {input_dto.credit_card_id} not found"
            )

        if credit_card.user_id != user_id:
            raise ValueError("Credit card does not belong to the specified user")

        # Create statement entity (validation happens in __post_init__)
        statement = MonthlyStatement(
            id=None,
            credit_card_id=input_dto.credit_card_id,
            billing_close_date=input_dto.billing_close_date,
            payment_due_date=input_dto.payment_due_date,
        )

        # Save
        saved_statement = self._statement_repository.save(statement)

        return MonthlyStatementResponseDTO(
            id=saved_statement.id,
            credit_card_id=saved_statement.credit_card_id,
            credit_card_name=credit_card.name,
            billing_close_date=saved_statement.billing_close_date,
            payment_due_date=saved_statement.payment_due_date,
        )
