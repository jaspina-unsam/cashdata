from dataclasses import dataclass

from app.domain.entities.credit_card import CreditCard
from app.domain.repositories.iunit_of_work import IUnitOfWork


@dataclass(frozen=True)
class ListCreditCardsByUserQuery:
    """Query to list credit cards by user"""

    user_id: int


class ListCreditCardsByUserUseCase:
    """
    Use case to list all credit cards for a user.
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: ListCreditCardsByUserQuery) -> list[CreditCard]:
        """
        Execute the use case to list credit cards by user.

        Args:
            query: The query containing user ID

        Returns:
            List of CreditCard entities for the user
        """
        with self.unit_of_work as uow:
            return uow.credit_cards.find_by_user_id(query.user_id)
