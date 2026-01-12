import pytest
from unittest.mock import Mock, MagicMock
from app.application.use_cases.create_bank_account_use_case import (
    CreateBankAccountUseCase,
)
from app.application.use_cases.list_bank_accounts_by_user_id import (
    ListBankAccountsUseCase,
)
from app.domain.entities.bank_account import BankAccount
from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.money import Currency
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.application.dtos.bank_account_dto import CreateBankAccountInputDTO, BankAccountResponseDTO


class TestCreateBankAccountUseCase:
    def test_should_create_bank_account_successfully(self):
        # Arrange
        mock_uow = Mock()
        mock_payment_method = PaymentMethod(
            id=1, user_id=1, type=PaymentMethodType.BANK_ACCOUNT, name="Test Bank Account"
        )
        mock_uow.payment_methods.save.return_value = mock_payment_method
        mock_bank_account = BankAccount(
            id=1,
            payment_method_id=1,
            primary_user_id=1,
            secondary_user_id=2,
            name="Test Bank Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="1234",
            currency=Currency.ARS,
        )
        mock_uow.bank_accounts.save.return_value = mock_bank_account
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = CreateBankAccountUseCase(mock_uow)
        input_dto = CreateBankAccountInputDTO(
            primary_user_id=1,
            secondary_user_id=2,
            name="Test Bank Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="1234",
            currency=Currency.ARS,
        )

        # Act
        result = use_case.execute(input_dto)

        # Assert
        mock_uow.payment_methods.save.assert_called_once()
        mock_uow.bank_accounts.save.assert_called_once()
        mock_uow.commit.assert_called_once()
        assert result == BankAccountResponseDTO(
            id=1,
            payment_method_id=1,
            primary_user_id=1,
            secondary_user_id=2,
            name="Test Bank Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="1234",
            currency=Currency.ARS,
        )

    def test_should_create_bank_account_without_secondary_user(self):
        # Arrange
        mock_uow = Mock()
        mock_payment_method = PaymentMethod(
            id=2, user_id=1, type=PaymentMethodType.BANK_ACCOUNT, name="Solo Account"
        )
        mock_uow.payment_methods.save.return_value = mock_payment_method
        mock_bank_account = BankAccount(
            id=2,
            payment_method_id=2,
            primary_user_id=1,
            secondary_user_id=None,
            name="Solo Account",
            bank="Solo Bank",
            account_type="CHECKING",
            last_four_digits="5678",
            currency=Currency.USD,
        )
        mock_uow.bank_accounts.save.return_value = mock_bank_account
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = CreateBankAccountUseCase(mock_uow)
        input_dto = CreateBankAccountInputDTO(
            primary_user_id=1,
            secondary_user_id=None,
            name="Solo Account",
            bank="Solo Bank",
            account_type="CHECKING",
            last_four_digits="5678",
            currency=Currency.USD,
        )

        # Act
        result = use_case.execute(input_dto)

        # Assert
        mock_uow.payment_methods.save.assert_called_once()
        mock_uow.bank_accounts.save.assert_called_once()
        mock_uow.commit.assert_called_once()
        assert result.secondary_user_id is None
        assert result.currency == Currency.USD

    def test_should_raise_error_when_payment_method_creation_fails(self):
        # Arrange
        mock_uow = Mock()
        mock_uow.payment_methods.save.side_effect = Exception("Database error")
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = CreateBankAccountUseCase(mock_uow)
        input_dto = CreateBankAccountInputDTO(
            primary_user_id=1,
            secondary_user_id=None,
            name="Test Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="1234",
            currency=Currency.ARS,
        )

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            use_case.execute(input_dto)

        mock_uow.payment_methods.save.assert_called_once()
        mock_uow.bank_accounts.save.assert_not_called()
        mock_uow.commit.assert_not_called()


class TestListBankAccountsUseCase:
    def test_should_return_bank_accounts_for_specific_user(self):
        # Arrange
        mock_uow = Mock()
        mock_bank_accounts = [
            BankAccount(
                id=1,
                payment_method_id=1,
                primary_user_id=1,
                secondary_user_id=None,
                name="Primary Account",
                bank="Bank A",
                account_type="SAVINGS",
                last_four_digits="1111",
                currency=Currency.ARS,
            ),
            BankAccount(
                id=2,
                payment_method_id=2,
                primary_user_id=2,
                secondary_user_id=1,  # User 1 is secondary here
                name="Shared Account",
                bank="Bank B",
                account_type="CHECKING",
                last_four_digits="2222",
                currency=Currency.USD,
            ),
        ]
        mock_uow.users.exists_by_id.return_value = True
        mock_uow.bank_accounts.find_by_user_id.return_value = mock_bank_accounts
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = ListBankAccountsUseCase(mock_uow)

        # Act
        result = use_case.execute(user_id=1)

        # Assert
        mock_uow.users.exists_by_id.assert_called_once_with(1)
        mock_uow.bank_accounts.find_by_user_id.assert_called_once_with(1)
        assert len(result) == 2
        assert all(isinstance(dto, BankAccountResponseDTO) for dto in result)

    def test_should_return_all_bank_accounts_when_no_user_specified(self):
        # Arrange
        mock_uow = Mock()
        mock_bank_accounts = [
            BankAccount(
                id=1,
                payment_method_id=1,
                primary_user_id=1,
                secondary_user_id=None,
                name="Account 1",
                bank="Bank A",
                account_type="SAVINGS",
                last_four_digits="1111",
                currency=Currency.ARS,
            ),
            BankAccount(
                id=2,
                payment_method_id=2,
                primary_user_id=2,
                secondary_user_id=None,
                name="Account 2",
                bank="Bank B",
                account_type="CHECKING",
                last_four_digits="2222",
                currency=Currency.USD,
            ),
        ]
        mock_uow.bank_accounts.find_all.return_value = mock_bank_accounts
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = ListBankAccountsUseCase(mock_uow)

        # Act
        result = use_case.execute()

        # Assert
        mock_uow.users.exists_by_id.assert_not_called()
        mock_uow.bank_accounts.find_all.assert_called_once()
        assert len(result) == 2
        assert all(isinstance(dto, BankAccountResponseDTO) for dto in result)

    def test_should_raise_error_when_user_does_not_exist(self):
        # Arrange
        mock_uow = Mock()
        mock_uow.users.exists_by_id.return_value = False
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = ListBankAccountsUseCase(mock_uow)

        # Act & Assert
        with pytest.raises(ValueError, match="User does not exist."):
            use_case.execute(user_id=999)

        mock_uow.users.exists_by_id.assert_called_once_with(999)
        mock_uow.bank_accounts.find_by_user_id.assert_not_called()

    def test_should_return_empty_list_when_no_accounts_for_user(self):
        # Arrange
        mock_uow = Mock()
        mock_uow.users.exists_by_id.return_value = True
        mock_uow.bank_accounts.find_by_user_id.return_value = []
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = ListBankAccountsUseCase(mock_uow)

        # Act
        result = use_case.execute(user_id=1)

        # Assert
        mock_uow.users.exists_by_id.assert_called_once_with(1)
        mock_uow.bank_accounts.find_by_user_id.assert_called_once_with(1)
        assert result == []

    def test_should_return_empty_list_when_no_accounts_in_system(self):
        # Arrange
        mock_uow = Mock()
        mock_uow.bank_accounts.find_all.return_value = []
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        use_case = ListBankAccountsUseCase(mock_uow)

        # Act
        result = use_case.execute()

        # Assert
        mock_uow.users.exists_by_id.assert_not_called()
        mock_uow.bank_accounts.find_all.assert_called_once()
        assert result == []
