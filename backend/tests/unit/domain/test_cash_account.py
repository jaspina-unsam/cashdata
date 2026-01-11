from dataclasses import FrozenInstanceError
from decimal import Decimal
from app.domain.entities.cash_account import CashAccount
from app.domain.value_objects.money import Currency, Money
import pytest


class TestCashAccount:
    def test_create_cash_account_success(self):
        """
        GIVEN: Valid parameters for creating a CashAccount
        WHEN: Creating a CashAccount
        THEN: Should create the CashAccount successfully
        """
        # Arrange & Act
        cash_account = CashAccount(
            id=None,
            payment_method_id=1,
            user_id=1,
            name="Efectivo",
            currency=Currency.ARS,
        )

        # Assert
        assert cash_account.id is None
        assert cash_account.user_id == 1
        assert cash_account.payment_method_id == 1
        assert cash_account.name == "Efectivo"
        assert cash_account.currency == Currency.ARS

    def test_create_cash_account_empty_name_raises(self):
        """
        GIVEN: An empty name for CashAccount
        WHEN: Creating a CashAccount
        THEN: Should raise ValueError
        """
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Cash account name cannot be empty"):
            CashAccount(
                id=None,
                payment_method_id=1,
                user_id=1,
                name="   ",
                currency=Currency.ARS,
            )

    def test_create_cash_account_name_too_long_raises(self):
        """
        GIVEN: A name that exceeds 100 characters
        WHEN: Creating a CashAccount
        THEN: Should raise ValueError
        """
        # Arrange, Act & Assert
        long_name = "A" * 101
        with pytest.raises(
            ValueError, match="Cash account name cannot exceed 100 characters"
        ):
            CashAccount(
                id=None,
                payment_method_id=1,
                user_id=1,
                name=long_name,
                currency=Currency.ARS,
            )

    def test_create_cash_account_invalid_currency_raises(self):
        """
        GIVEN: An invalid currency type
        WHEN: Creating a CashAccount
        THEN: Should raise ValueError
        """
        # Arrange, Act & Assert
        with pytest.raises(
            ValueError, match="Currency must be a valid Currency enum value"
        ):
            CashAccount(
                id=None,
                payment_method_id=1,
                user_id=1,
                name="Efectivo",
                currency="INVALID_CURRENCY",  # type: ignore
            )

    def test_cash_account_equality(self):
        """
        GIVEN: Two CashAccount instances
        WHEN: Comparing them for equality
        THEN: Should be equal if IDs match, otherwise not equal
        """
        # Arrange
        cash_account1 = CashAccount(
            id=1,
            payment_method_id=1,
            user_id=1,
            name="Efectivo",
            currency=Currency.ARS,
        )
        cash_account2 = CashAccount(
            id=1,
            payment_method_id=2,
            user_id=2,
            name="Ahorros",
            currency=Currency.USD,
        )
        cash_account3 = CashAccount(
            id=2,
            payment_method_id=1,
            user_id=1,
            name="Efectivo",
            currency=Currency.ARS,
        )

        # Act & Assert
        assert cash_account1 == cash_account2  # Same ID
        assert cash_account1 != cash_account3  # Different ID

    def test_new_cash_accounts_not_equal(self):
        """
        GIVEN: Two new CashAccount instances (id=None)
        WHEN: Comparing them for equality
        THEN: Should not be equal (different instances)
        """
        # Arrange
        cash_account1 = CashAccount(
            id=None,
            payment_method_id=1,
            user_id=1,
            name="Efectivo",
            currency=Currency.ARS,
        )
        cash_account2 = CashAccount(
            id=None,
            payment_method_id=1,
            user_id=1,
            name="Efectivo",
            currency=Currency.ARS,
        )

        # Act & Assert
        assert cash_account1 != cash_account2

    def test_cash_account_immutable(self):
        """
        GIVEN: A CashAccount instance
        WHEN: Trying to modify a field
        THEN: Should raise FrozenInstanceError
        """
        # Arrange
        cash_account = CashAccount(
            id=1,
            payment_method_id=1,
            user_id=1,
            name="Efectivo",
            currency=Currency.ARS,
        )

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            cash_account.name = "Nuevo Nombre"

    def test_cash_account_name_whitespace_normalization(self):
        """
        GIVEN: A CashAccount name with leading/trailing whitespace
        WHEN: Creating a CashAccount
        THEN: The name should be normalized (whitespace stripped)
        """
        # Arrange & Act
        cash_account = CashAccount(
            id=None,
            payment_method_id=1,
            user_id=1,
            name="   Efectivo   ",
            currency=Currency.ARS,
        )

        # Assert
        assert cash_account.name == "Efectivo"

    def test_cash_account_hashing(self):
        """
        GIVEN: A CashAccount instance
        WHEN: Getting its hash
        THEN: Should return a hash based on its ID
        """
        # Arrange
        cash_account = CashAccount(
            id=1,
            payment_method_id=1,
            user_id=1,
            name="Efectivo",
            currency=Currency.ARS,
        )

        # Act
        cash_account_hash = hash(cash_account)

        # Assert
        assert cash_account_hash == hash(1)
