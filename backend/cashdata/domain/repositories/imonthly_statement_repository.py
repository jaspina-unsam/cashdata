"""Monthly statement repository interface."""

from abc import ABC, abstractmethod
from datetime import date

from cashdata.domain.entities.monthly_statement import MonthlyStatement


class IMonthlyStatementRepository(ABC):
    """Repository interface for monthly statements."""

    @abstractmethod
    def find_by_id(self, statement_id: int) -> MonthlyStatement | None:
        """Find a monthly statement by its ID.

        Args:
            statement_id: The statement's ID

        Returns:
            The monthly statement if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_credit_card_id(
        self, credit_card_id: int, include_future: bool = False
    ) -> list[MonthlyStatement]:
        """Find all statements for a credit card.

        Args:
            credit_card_id: The credit card's ID
            include_future: Whether to include statements with future payment dates

        Returns:
            List of monthly statements ordered by payment_due_date descending
        """
        pass

    @abstractmethod
    def find_all_by_user_id(
        self, user_id: int, include_future: bool = False
    ) -> list[MonthlyStatement]:
        """Find all statements for all credit cards owned by a user.

        Args:
            user_id: The user's ID
            include_future: Whether to include statements with future payment dates

        Returns:
            List of monthly statements ordered by payment_due_date descending
        """
        pass

    @abstractmethod
    def save(self, statement: MonthlyStatement) -> MonthlyStatement:
        """Save a monthly statement (create or update).

        Args:
            statement: The monthly statement to save

        Returns:
            The saved monthly statement with ID populated
        """
        pass

    @abstractmethod
    def get_previous_statement(
        self, credit_card_id: int, billing_close_date: date
    ) -> MonthlyStatement | None:
        """Get the previous statement for a credit card.

        Args:
            credit_card_id: The credit card's ID
            billing_close_date: The current statement's close date

        Returns:
            The previous statement (with earlier close date), or None if this is the first
        """
        pass
