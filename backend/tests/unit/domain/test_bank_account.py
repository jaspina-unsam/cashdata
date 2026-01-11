import pytest
from dataclasses import FrozenInstanceError

from app.domain.entities.bank_account import BankAccount
from app.domain.value_objects.money import Currency
from app.domain.exceptions.domain_exceptions import (
    BankAccountNameError,
    BankAccountUserError,
)


class TestBankAccount:
    """Test suite for BankAccount entity."""

    def test_creation_valid_complete(self):
        """Test creating a valid BankAccount with all fields."""
        ba = BankAccount(
            id=1,
            payment_method_id=10,
            primary_user_id=100,
            secondary_user_id=200,
            name="Main Savings",
            bank="Bank of America",
            account_type="CHECKING",
            last_four_digits="1234",
            currency=Currency.ARS,
        )
        assert ba.id == 1
        assert ba.payment_method_id == 10
        assert ba.primary_user_id == 100
        assert ba.secondary_user_id == 200
        assert ba.name == "Main Savings"
        assert ba.bank == "Bank of America"
        assert ba.account_type == "CHECKING"
        assert ba.last_four_digits == "1234"
        assert ba.currency == Currency.ARS

    def test_creation_valid_minimal(self):
        """Test creating a valid BankAccount with minimal required fields."""
        ba = BankAccount(
            id=None,
            payment_method_id=20,
            primary_user_id=300,
            secondary_user_id=None,
            name="Emergency Fund",
            bank="Chase",
            account_type="SAVINGS",
            last_four_digits="5678",
            currency=Currency.USD,
        )
        assert ba.id is None
        assert ba.payment_method_id == 20
        assert ba.primary_user_id == 300
        assert ba.secondary_user_id is None
        assert ba.name == "Emergency Fund"
        assert ba.bank == "Chase"
        assert ba.account_type == "SAVINGS"
        assert ba.last_four_digits == "5678"
        assert ba.currency == Currency.USD

    def test_creation_currency_string_conversion(self):
        """Test that currency string is converted to Currency enum."""
        ba = BankAccount(
            id=2,
            payment_method_id=30,
            primary_user_id=400,
            secondary_user_id=None,
            name="Test Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="9999",
            currency="USD",
        )
        assert ba.currency == Currency.USD
        assert isinstance(ba.currency, Currency)

    def test_name_validation_empty_string(self):
        """Test that empty name raises BankAccountNameError."""
        with pytest.raises(BankAccountNameError, match="Bank account name cannot be empty"):
            BankAccount(
                id=3,
                payment_method_id=40,
                primary_user_id=500,
                secondary_user_id=None,
                name="",
                bank="Test Bank",
                account_type="SAVINGS",
                last_four_digits="1111",
                currency=Currency.ARS,
            )

    def test_name_validation_whitespace_only(self):
        """Test that whitespace-only name raises BankAccountNameError."""
        with pytest.raises(BankAccountNameError, match="Bank account name cannot be empty"):
            BankAccount(
                id=4,
                payment_method_id=50,
                primary_user_id=600,
                secondary_user_id=None,
                name="   ",
                bank="Test Bank",
                account_type="SAVINGS",
                last_four_digits="2222",
                currency=Currency.ARS,
            )

    def test_name_validation_too_long(self):
        """Test that name longer than 100 characters raises BankAccountNameError."""
        long_name = "A" * 101
        with pytest.raises(BankAccountNameError, match="Bank account name cannot exceed 100 characters"):
            BankAccount(
                id=5,
                payment_method_id=60,
                primary_user_id=700,
                secondary_user_id=None,
                name=long_name,
                bank="Test Bank",
                account_type="SAVINGS",
                last_four_digits="3333",
                currency=Currency.ARS,
            )

    def test_name_validation_max_length(self):
        """Test that name exactly 100 characters is valid."""
        max_name = "A" * 100
        ba = BankAccount(
            id=6,
            payment_method_id=70,
            primary_user_id=800,
            secondary_user_id=None,
            name=max_name,
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="4444",
            currency=Currency.ARS,
        )
        assert ba.name == max_name
        assert len(ba.name) == 100

    def test_name_normalization_leading_trailing_whitespace(self):
        """Test that leading and trailing whitespace is stripped from name."""
        ba = BankAccount(
            id=7,
            payment_method_id=80,
            primary_user_id=900,
            secondary_user_id=None,
            name="  My Account  ",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="5555",
            currency=Currency.ARS,
        )
        assert ba.name == "My Account"

    def test_user_validation_same_primary_secondary(self):
        """Test that same primary and secondary user raises BankAccountUserError."""
        with pytest.raises(BankAccountUserError, match="Primary and secondary user cannot be the same"):
            BankAccount(
                id=8,
                payment_method_id=90,
                primary_user_id=1000,
                secondary_user_id=1000,
                name="Shared Account",
                bank="Test Bank",
                account_type="SAVINGS",
                last_four_digits="6666",
                currency=Currency.ARS,
            )

    def test_user_validation_different_users(self):
        """Test that different primary and secondary users is valid."""
        ba = BankAccount(
            id=9,
            payment_method_id=100,
            primary_user_id=1100,
            secondary_user_id=1200,
            name="Joint Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="7777",
            currency=Currency.ARS,
        )
        assert ba.primary_user_id == 1100
        assert ba.secondary_user_id == 1200

    def test_currency_validation_invalid_type(self):
        """Test that invalid currency type raises ValueError."""
        with pytest.raises(ValueError):
            BankAccount(
                id=10,
                payment_method_id=110,
                primary_user_id=1300,
                secondary_user_id=None,
                name="Test Account",
                bank="Test Bank",
                account_type="SAVINGS",
                last_four_digits="8888",
                currency="INVALID",
            )

    def test_has_access_primary_user(self):
        """Test has_access returns True for primary user."""
        ba = BankAccount(
            id=11,
            payment_method_id=120,
            primary_user_id=1400,
            secondary_user_id=1500,
            name="Test Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="9999",
            currency=Currency.ARS,
        )
        assert ba.has_access(1400) is True

    def test_has_access_secondary_user(self):
        """Test has_access returns True for secondary user."""
        ba = BankAccount(
            id=12,
            payment_method_id=130,
            primary_user_id=1600,
            secondary_user_id=1700,
            name="Test Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="0000",
            currency=Currency.ARS,
        )
        assert ba.has_access(1700) is True

    def test_has_access_no_access(self):
        """Test has_access returns False for user without access."""
        ba = BankAccount(
            id=13,
            payment_method_id=140,
            primary_user_id=1800,
            secondary_user_id=1900,
            name="Test Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="1111",
            currency=Currency.ARS,
        )
        assert ba.has_access(2000) is False

    def test_has_access_none_secondary_user(self):
        """Test has_access when secondary_user_id is None."""
        ba = BankAccount(
            id=14,
            payment_method_id=150,
            primary_user_id=2100,
            secondary_user_id=None,
            name="Test Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="2222",
            currency=Currency.ARS,
        )
        assert ba.has_access(2100) is True
        assert ba.has_access(2200) is False

    def test_equality_same_id(self):
        """Test that BankAccounts with same ID are equal."""
        ba1 = BankAccount(
            id=15,
            payment_method_id=160,
            primary_user_id=2300,
            secondary_user_id=None,
            name="Account 1",
            bank="Bank A",
            account_type="SAVINGS",
            last_four_digits="3333",
            currency=Currency.ARS,
        )
        ba2 = BankAccount(
            id=15,
            payment_method_id=170,
            primary_user_id=2400,
            secondary_user_id=2500,
            name="Account 2",
            bank="Bank B",
            account_type="CHECKING",
            last_four_digits="4444",
            currency=Currency.USD,
        )
        assert ba1 == ba2

    def test_equality_different_id(self):
        """Test that BankAccounts with different IDs are not equal."""
        ba1 = BankAccount(
            id=16,
            payment_method_id=180,
            primary_user_id=2600,
            secondary_user_id=None,
            name="Account 1",
            bank="Bank A",
            account_type="SAVINGS",
            last_four_digits="5555",
            currency=Currency.ARS,
        )
        ba2 = BankAccount(
            id=17,
            payment_method_id=180,
            primary_user_id=2600,
            secondary_user_id=None,
            name="Account 1",
            bank="Bank A",
            account_type="SAVINGS",
            last_four_digits="5555",
            currency=Currency.ARS,
        )
        assert ba1 != ba2

    def test_equality_none_id(self):
        """Test equality with None IDs."""
        ba1 = BankAccount(
            id=None,
            payment_method_id=190,
            primary_user_id=2700,
            secondary_user_id=None,
            name="Account 1",
            bank="Bank A",
            account_type="SAVINGS",
            last_four_digits="6666",
            currency=Currency.ARS,
        )
        ba2 = BankAccount(
            id=None,
            payment_method_id=190,
            primary_user_id=2700,
            secondary_user_id=None,
            name="Account 1",
            bank="Bank A",
            account_type="SAVINGS",
            last_four_digits="6666",
            currency=Currency.ARS,
        )
        # Different objects with None ID should not be equal
        assert ba1 != ba2
        # But same object should be equal to itself
        assert ba1 == ba1

    def test_equality_different_types(self):
        """Test equality with different types."""
        ba = BankAccount(
            id=18,
            payment_method_id=200,
            primary_user_id=2800,
            secondary_user_id=None,
            name="Account",
            bank="Bank",
            account_type="SAVINGS",
            last_four_digits="7777",
            currency=Currency.ARS,
        )
        assert ba != "not a bank account"
        assert ba != 18

    def test_hash_same_id(self):
        """Test that BankAccounts with same ID have same hash."""
        ba1 = BankAccount(
            id=19,
            payment_method_id=210,
            primary_user_id=2900,
            secondary_user_id=None,
            name="Account 1",
            bank="Bank A",
            account_type="SAVINGS",
            last_four_digits="8888",
            currency=Currency.ARS,
        )
        ba2 = BankAccount(
            id=19,
            payment_method_id=220,
            primary_user_id=3000,
            secondary_user_id=3100,
            name="Account 2",
            bank="Bank B",
            account_type="CHECKING",
            last_four_digits="9999",
            currency=Currency.USD,
        )
        assert hash(ba1) == hash(ba2)

    def test_hash_different_id(self):
        """Test that BankAccounts with different IDs have different hashes."""
        ba1 = BankAccount(
            id=20,
            payment_method_id=230,
            primary_user_id=3200,
            secondary_user_id=None,
            name="Account 1",
            bank="Bank A",
            account_type="SAVINGS",
            last_four_digits="0000",
            currency=Currency.ARS,
        )
        ba2 = BankAccount(
            id=21,
            payment_method_id=230,
            primary_user_id=3200,
            secondary_user_id=None,
            name="Account 1",
            bank="Bank A",
            account_type="SAVINGS",
            last_four_digits="0000",
            currency=Currency.ARS,
        )
        assert hash(ba1) != hash(ba2)

    def test_hash_none_id(self):
        """Test hash with None ID uses object id."""
        ba1 = BankAccount(
            id=None,
            payment_method_id=240,
            primary_user_id=3300,
            secondary_user_id=None,
            name="Account",
            bank="Bank",
            account_type="SAVINGS",
            last_four_digits="1111",
            currency=Currency.ARS,
        )
        ba2 = BankAccount(
            id=None,
            payment_method_id=240,
            primary_user_id=3300,
            secondary_user_id=None,
            name="Account",
            bank="Bank",
            account_type="SAVINGS",
            last_four_digits="1111",
            currency=Currency.ARS,
        )
        # Different objects with None ID should have different hashes
        assert hash(ba1) != hash(ba2)

    def test_frozen_dataclass(self):
        """Test that BankAccount is frozen and cannot be modified."""
        ba = BankAccount(
            id=22,
            payment_method_id=250,
            primary_user_id=3400,
            secondary_user_id=None,
            name="Frozen Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="2222",
            currency=Currency.ARS,
        )
        with pytest.raises(FrozenInstanceError):
            ba.name = "Modified Name"

    def test_repr(self):
        """Test string representation of BankAccount."""
        ba = BankAccount(
            id=23,
            payment_method_id=260,
            primary_user_id=3500,
            secondary_user_id=3600,
            name="Test Account",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="3333",
            currency=Currency.ARS,
        )
        repr_str = repr(ba)
        assert "BankAccount" in repr_str
        assert "id=23" in repr_str
        assert "name='Test Account'" in repr_str
        assert "currency=<Currency.ARS: 'ARS'>" in repr_str
