import pytest
from unittest.mock import Mock, MagicMock
from app.application.use_cases.create_cash_account_use_case import (
    CreateCashAccountUseCase,
)
from app.application.use_cases.delete_cash_account_use_case import (
    DeleteCashAccountUseCase,
)
from app.application.use_cases.list_cash_accounts_use_case import (
    ListAllCashAccountsUseCase,
)
from app.application.use_cases.list_cash_accounts_by_user_id_use_case import (
    ListCashAccountsByUserIdUseCase,
)
from app.domain.entities.cash_account import CashAccount
from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.money import Currency
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.application.dtos.cash_account_dto import CreateCashAccountInputDTO, CashAccountResponseDTO


class TestCreateCashAccountUseCase:
    def test_should_create_cash_account_successfully(self):
        # Arrange
        mock_uow = Mock()
        mock_uow.cash_accounts.exists_by_user_id_and_currency.return_value = False
        mock_payment_method = PaymentMethod(
            id=1, user_id=1, type=PaymentMethodType.CASH, name="Test Account"
        )
        mock_uow.payment_methods.save.return_value = mock_payment_method
        mock_cash_account = CashAccount(
            id=1,
            payment_method_id=1,
            user_id=1,
            name="Test Account",
            currency=Currency.ARS,
        )
        mock_uow.cash_accounts.save.return_value = mock_cash_account
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = CreateCashAccountUseCase(mock_uow)
        input_dto = CreateCashAccountInputDTO(
            user_id=1, name="Test Account", currency=Currency.ARS
        )

        # Act
        result = use_case.execute(input_dto)

        # Assert
        mock_uow.cash_accounts.exists_by_user_id_and_currency.assert_called_once_with(
            1, "ARS"
        )
        mock_uow.payment_methods.save.assert_called_once()
        mock_uow.cash_accounts.save.assert_called_once()
        mock_uow.commit.assert_called_once()
        assert result == CashAccountResponseDTO(
            id=1, user_id=1, name="Test Account", currency="ARS"
        )

    def test_should_raise_error_when_cash_account_already_exists_for_currency(self):
        # Arrange
        mock_uow = Mock()
        mock_uow.cash_accounts.exists_by_user_id_and_currency.return_value = True
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = CreateCashAccountUseCase(mock_uow)
        input_dto = CreateCashAccountInputDTO(
            user_id=1, name="Test Account", currency=Currency.ARS
        )

        # Act & Assert
        with pytest.raises(
            ValueError,
            match="Cash account with this currency already exists for the user.",
        ):
            use_case.execute(input_dto)

        mock_uow.cash_accounts.exists_by_user_id_and_currency.assert_called_once_with(
            1, "ARS"
        )
        mock_uow.payment_methods.save.assert_not_called()
        mock_uow.cash_accounts.save.assert_not_called()
        mock_uow.commit.assert_not_called()


class TestDeleteCashAccountUseCase:
    def test_should_delete_cash_account_successfully(self):
        # Arrange
        mock_uow = Mock()
        mock_cash_account = CashAccount(
            id=1,
            payment_method_id=1,
            user_id=1,
            name="Test Account",
            currency=Currency.ARS,
        )
        mock_uow.cash_accounts.find_by_id.return_value = mock_cash_account
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = DeleteCashAccountUseCase(mock_uow)

        # Act
        use_case.execute(1)

        # Assert
        mock_uow.cash_accounts.find_by_id.assert_called_once_with(1)
        mock_uow.cash_accounts.delete.assert_called_once_with(mock_cash_account)
        mock_uow.commit.assert_called_once()

    def test_should_raise_error_when_cash_account_not_found(self):
        # Arrange
        mock_uow = Mock()
        mock_uow.cash_accounts.find_by_id.return_value = None
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = DeleteCashAccountUseCase(mock_uow)

        # Act & Assert
        with pytest.raises(ValueError, match="Cash account with ID 1 not found"):
            use_case.execute(1)

        mock_uow.cash_accounts.find_by_id.assert_called_once_with(1)
        mock_uow.cash_accounts.delete.assert_not_called()
        mock_uow.commit.assert_not_called()


class TestListAllCashAccountsUseCase:
    def test_should_return_all_cash_accounts(self):
        # Arrange
        mock_uow = Mock()
        mock_cash_accounts = [
            CashAccount(
                id=1,
                payment_method_id=1,
                user_id=1,
                name="Account 1",
                currency=Currency.ARS,
            ),
            CashAccount(
                id=2,
                payment_method_id=2,
                user_id=2,
                name="Account 2",
                currency=Currency.USD,
            ),
        ]
        mock_uow.cash_accounts.find_all.return_value = mock_cash_accounts
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = ListAllCashAccountsUseCase(mock_uow)

        # Act
        result = use_case.execute()

        # Assert
        mock_uow.cash_accounts.find_all.assert_called_once()
        assert len(result) == 2
        # Assuming the mapper returns DTOs, but since mocked, just check call


class TestListCashAccountsByUserIdUseCase:
    def test_should_return_cash_accounts_for_user(self):
        # Arrange
        mock_uow = Mock()
        mock_cash_accounts = [
            CashAccount(
                id=1,
                payment_method_id=1,
                user_id=1,
                name="Account 1",
                currency=Currency.ARS,
            ),
            CashAccount(
                id=2,
                payment_method_id=2,
                user_id=1,
                name="Account 2",
                currency=Currency.USD,
            ),
        ]
        mock_uow.cash_accounts.find_by_user_id.return_value = mock_cash_accounts
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = ListCashAccountsByUserIdUseCase(mock_uow)

        # Act
        result = use_case.execute(1)

        # Assert
        mock_uow.cash_accounts.find_by_user_id.assert_called_once_with(1)
        assert len(result) == 2

    def test_should_return_empty_list_when_no_accounts_for_user(self):
        # Arrange
        mock_uow = Mock()
        mock_uow.cash_accounts.find_by_user_id.return_value = []
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = ListCashAccountsByUserIdUseCase(mock_uow)

        # Act
        result = use_case.execute(999)

        # Assert
        mock_uow.cash_accounts.find_by_user_id.assert_called_once_with(999)
        assert result == []
