from dataclasses import dataclass
from typing import List

from app.application.exceptions.application_exceptions import (
    CreditCardNotFoundError,
    CreditCardOwnerMismatchError,
)
from app.domain.entities.monthly_statement import MonthlyStatement
from app.domain.repositories.iunit_of_work import IUnitOfWork


@dataclass(frozen=True)
class ListStatementByCreditCardQuery:
    user_id: int
    credit_card_id: int


class ListStatementByCreditCardUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, query: ListStatementByCreditCardQuery) -> List[MonthlyStatement]:
        """
        Loads the credit card and verifies the user owns it

        Calls the repository to find statements by credit card id

        Args:
            query: containing user_id and credit_card_id

        Returns:
            List[Statement]

        Raises:
            CreditCardNotFoundError, CreditCardNotFoundError
        """
        with self._uow as uow:
            credit_card = uow.credit_cards.find_by_id(query.credit_card_id)
            if not credit_card:
                raise CreditCardNotFoundError(
                    f"Credit card with ID {query.credit_card_id} not found"
                )

            if credit_card.user_id != query.user_id:
                raise CreditCardOwnerMismatchError(
                    f"Credit card {query.credit_card_id} does not belong to user {query.user_id}"
                )

            statements = uow.monthly_statements.find_by_credit_card_id(query.credit_card_id)

            return sorted(statements, key=lambda x: x.due_date)