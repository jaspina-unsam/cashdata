from dataclasses import dataclass

from app.application.exceptions.application_exceptions import (
    MonthlyStatementNotFoundError,
    CreditCardOwnerMismatchError,
)
from app.domain.repositories.iunit_of_work import IUnitOfWork


@dataclass(frozen=True)
class DeleteStatementCommand:
    """Command to delete a monthly statement"""

    statement_id: int
    user_id: int


class DeleteStatementUseCase:
    """Use case to delete an existing monthly statement."""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, command: DeleteStatementCommand) -> None:
        """Delete a monthly statement after authorization checks.

        Raises:
            MonthlyStatementNotFoundError: If statement doesn't exist
            CreditCardOwnerMismatchError: If the statement's credit card doesn't belong to user
        """
        with self._uow:
            statement = self._uow.monthly_statements.find_by_id(command.statement_id)
            if statement is None:
                raise MonthlyStatementNotFoundError(
                    f"Statement with ID {command.statement_id} not found"
                )

            # Verify ownership via credit card
            credit_card = self._uow.credit_cards.find_by_id(statement.credit_card_id)
            if not credit_card or credit_card.user_id != command.user_id:
                raise CreditCardOwnerMismatchError(
                    f"Statement {command.statement_id} does not belong to user {command.user_id}"
                )

            deleted = self._uow.monthly_statements.delete(command.statement_id)
            if not deleted:
                raise MonthlyStatementNotFoundError(
                    f"Statement with ID {command.statement_id} not found during deletion"
                )

            self._uow.commit()
