import pytest
from unittest.mock import MagicMock

from app.application.use_cases.delete_statement_use_case import (
    DeleteStatementUseCase,
    DeleteStatementCommand,
)
from app.application.exceptions.application_exceptions import (
    MonthlyStatementNotFoundError,
    CreditCardOwnerMismatchError,
)
from app.domain.entities.monthly_statement import MonthlyStatement


class TestDeleteStatementUseCase:
    def test_should_delete_statement_when_user_owns_it(self):
        mock_uow = MagicMock()
        mock_statement_repo = MagicMock()
        mock_credit_card_repo = MagicMock()

        mock_uow.monthly_statements = mock_statement_repo
        mock_uow.credit_cards = mock_credit_card_repo

        statement = MonthlyStatement(
            id=1,
            credit_card_id=10,
            start_date="2025-01-01",
            closing_date="2025-01-15",
            due_date="2025-01-20",
        )

        mock_statement_repo.find_by_id.return_value = statement
        mock_credit_card_repo.find_by_id.return_value = MagicMock(user_id=1)
        mock_statement_repo.delete.return_value = True

        use_case = DeleteStatementUseCase(mock_uow)
        cmd = DeleteStatementCommand(statement_id=1, user_id=1)

        use_case.execute(cmd)

        mock_statement_repo.find_by_id.assert_called_once_with(1)
        mock_statement_repo.delete.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()

    def test_should_raise_not_found_if_statement_missing(self):
        mock_uow = MagicMock()
        mock_statement_repo = MagicMock()
        mock_uow.monthly_statements = mock_statement_repo
        mock_statement_repo.find_by_id.return_value = None

        use_case = DeleteStatementUseCase(mock_uow)
        cmd = DeleteStatementCommand(statement_id=1, user_id=1)

        with pytest.raises(MonthlyStatementNotFoundError):
            use_case.execute(cmd)

        mock_statement_repo.delete.assert_not_called()
        mock_uow.commit.assert_not_called()

    def test_should_raise_forbidden_if_user_doesnt_own_card(self):
        mock_uow = MagicMock()
        mock_statement_repo = MagicMock()
        mock_credit_card_repo = MagicMock()

        mock_uow.monthly_statements = mock_statement_repo
        mock_uow.credit_cards = mock_credit_card_repo

        statement = MonthlyStatement(
            id=1,
            credit_card_id=10,
            start_date="2025-01-01",
            closing_date="2025-01-15",
            due_date="2025-01-20",
        )

        mock_statement_repo.find_by_id.return_value = statement
        mock_credit_card_repo.find_by_id.return_value = MagicMock(user_id=999)  # different user

        use_case = DeleteStatementUseCase(mock_uow)
        cmd = DeleteStatementCommand(statement_id=1, user_id=1)

        with pytest.raises(CreditCardOwnerMismatchError):
            use_case.execute(cmd)

        mock_statement_repo.delete.assert_not_called()
        mock_uow.commit.assert_not_called()
