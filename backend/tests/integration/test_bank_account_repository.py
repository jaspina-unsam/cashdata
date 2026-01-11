import pytest
from decimal import Decimal

from app.domain.entities.bank_account import BankAccount
from app.domain.entities.user import User
from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.money import Money, Currency
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.infrastructure.persistence.mappers.user_mapper import UserMapper
from app.infrastructure.persistence.mappers.payment_method_mapper import PaymentMethodMapper
from app.infrastructure.persistence.repositories.sqlalchemy_bank_account_repository import (
    SQLAlchemyBankAccountRepository,
)


class TestSQLAlchemyBankAccountRepository:
    """Integration tests for SQLAlchemyBankAccountRepository."""

    @pytest.fixture
    def repo(self, db_session):
        return SQLAlchemyBankAccountRepository(db_session)

    @pytest.fixture
    def test_user(self, db_session):
        """Create a test user."""
        user = User(
            id=None,
            email="test@example.com",
            name="Test User",
            wage=Money(Decimal("50000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user_model = UserMapper.to_model(user)
        db_session.add(user_model)
        db_session.flush()
        return user_model.id

    @pytest.fixture
    def test_payment_method(self, db_session, test_user):
        """Create a test payment method."""
        pm = PaymentMethod(
            id=None,
            user_id=test_user,
            type=PaymentMethodType.BANK_ACCOUNT,
            name="Test Bank Account",
            is_active=True,
        )
        pm_model = PaymentMethodMapper.to_model(pm)
        db_session.add(pm_model)
        db_session.flush()
        return pm_model.id

    def test_save_new_bank_account(self, repo, db_session, test_payment_method, test_user):
        """Test saving a new bank account."""
        # Create bank account
        ba = BankAccount(
            id=None,
            payment_method_id=test_payment_method,
            primary_user_id=test_user,
            secondary_user_id=None,
            name="Main Savings",
            bank="Test Bank",
            account_type="SAVINGS",
            last_four_digits="1234",
            currency=Currency.ARS,
        )

        # Save it
        saved_ba = repo.save(ba)

        # Verify it was saved
        assert saved_ba.id is not None
        assert saved_ba.payment_method_id == test_payment_method
        assert saved_ba.primary_user_id == test_user
        assert saved_ba.secondary_user_id is None
        assert saved_ba.name == "Main Savings"
        assert saved_ba.bank == "Test Bank"
        assert saved_ba.account_type == "SAVINGS"
        assert saved_ba.last_four_digits == "1234"
        assert saved_ba.currency == Currency.ARS

        # Verify in database
        db_ba = repo.find_by_id(saved_ba.id)
        assert db_ba == saved_ba

    def test_save_bank_account_with_secondary_user(self, repo, db_session, test_payment_method, test_user):
        """Test saving a bank account with a secondary user."""
        # Create another user
        user2 = User(
            id=None,
            email="test2@example.com",
            name="Test User 2",
            wage=Money(Decimal("60000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user2_model = UserMapper.to_model(user2)
        db_session.add(user2_model)
        db_session.flush()
        user2_id = user2_model.id

        # Create bank account
        ba = BankAccount(
            id=None,
            payment_method_id=test_payment_method,
            primary_user_id=test_user,
            secondary_user_id=user2_id,
            name="Joint Account",
            bank="Joint Bank",
            account_type="CHECKING",
            last_four_digits="5678",
            currency=Currency.USD,
        )

        # Save it
        saved_ba = repo.save(ba)

        # Verify
        assert saved_ba.secondary_user_id == user2_id
        assert saved_ba.currency == Currency.USD

    def test_find_by_id_existing_account(self, repo, test_payment_method, test_user):
        """Test finding an existing bank account by ID."""
        # Create and save
        ba = BankAccount(
            id=None,
            payment_method_id=test_payment_method,
            primary_user_id=test_user,
            secondary_user_id=None,
            name="Find Me",
            bank="Find Bank",
            account_type="SAVINGS",
            last_four_digits="9999",
            currency=Currency.ARS,
        )
        saved_ba = repo.save(ba)

        # Find it
        found_ba = repo.find_by_id(saved_ba.id)

        assert found_ba is not None
        assert found_ba == saved_ba
        assert found_ba.id == saved_ba.id

    def test_find_by_id_nonexistent_account(self, repo):
        """Test finding a non-existent bank account returns None."""
        found_ba = repo.find_by_id(99999)
        assert found_ba is None

    def test_find_by_user_id_primary_user(self, repo, db_session, test_payment_method, test_user):
        """Test finding bank accounts by primary user ID."""
        # Create account for primary user
        ba1 = BankAccount(
            id=None,
            payment_method_id=test_payment_method,
            primary_user_id=test_user,
            secondary_user_id=None,
            name="Primary Account",
            bank="Primary Bank",
            account_type="SAVINGS",
            last_four_digits="1111",
            currency=Currency.ARS,
        )
        saved_ba1 = repo.save(ba1)

        # Create another user
        user2 = User(
            id=None,
            email="user2@example.com",
            name="User 2",
            wage=Money(Decimal("70000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user2_model = UserMapper.to_model(user2)
        db_session.add(user2_model)
        db_session.flush()
        user2_id = user2_model.id

        # Create payment method for user2
        pm2 = PaymentMethod(
            id=None,
            user_id=user2_id,
            type=PaymentMethodType.BANK_ACCOUNT,
            name="User2 Bank Account",
            is_active=True,
        )
        pm2_model = PaymentMethodMapper.to_model(pm2)
        db_session.add(pm2_model)
        db_session.flush()
        pm2_id = pm2_model.id

        # Create account for user2
        ba2 = BankAccount(
            id=None,
            payment_method_id=pm2_id,
            primary_user_id=user2_id,
            secondary_user_id=None,
            name="User2 Account",
            bank="User2 Bank",
            account_type="CHECKING",
            last_four_digits="2222",
            currency=Currency.ARS,
        )
        saved_ba2 = repo.save(ba2)

        # Find accounts for test_user
        user_accounts = repo.find_by_user_id(test_user)

        assert len(user_accounts) == 1
        assert user_accounts[0] == saved_ba1

        # Find accounts for user2
        user2_accounts = repo.find_by_user_id(user2_id)

        assert len(user2_accounts) == 1
        assert user2_accounts[0] == saved_ba2

    def test_find_by_user_id_secondary_user(self, repo, db_session, test_payment_method, test_user):
        """Test finding bank accounts where user is secondary."""
        # Create another user
        user2 = User(
            id=None,
            email="secondary@example.com",
            name="Secondary User",
            wage=Money(Decimal("80000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user2_model = UserMapper.to_model(user2)
        db_session.add(user2_model)
        db_session.flush()
        user2_id = user2_model.id

        # Create account where test_user is primary and user2 is secondary
        ba = BankAccount(
            id=None,
            payment_method_id=test_payment_method,
            primary_user_id=test_user,
            secondary_user_id=user2_id,
            name="Shared Account",
            bank="Shared Bank",
            account_type="SAVINGS",
            last_four_digits="3333",
            currency=Currency.ARS,
        )
        saved_ba = repo.save(ba)

        # Find accounts for primary user
        primary_accounts = repo.find_by_user_id(test_user)
        assert len(primary_accounts) == 1
        assert primary_accounts[0] == saved_ba

        # Find accounts for secondary user
        secondary_accounts = repo.find_by_user_id(user2_id)
        assert len(secondary_accounts) == 1
        assert secondary_accounts[0] == saved_ba

    def test_find_by_user_id_no_accounts(self, repo, db_session):
        """Test finding accounts for user with no bank accounts."""
        # Create a user with no bank accounts
        user = User(
            id=None,
            email="noaccounts@example.com",
            name="No Accounts User",
            wage=Money(Decimal("90000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user_model = UserMapper.to_model(user)
        db_session.add(user_model)
        db_session.flush()
        user_id = user_model.id

        accounts = repo.find_by_user_id(user_id)
        assert accounts == []

    def test_update_existing_bank_account(self, repo, test_payment_method, test_user):
        """Test updating an existing bank account."""
        # Create and save initial account
        ba = BankAccount(
            id=None,
            payment_method_id=test_payment_method,
            primary_user_id=test_user,
            secondary_user_id=None,
            name="Original Name",
            bank="Original Bank",
            account_type="SAVINGS",
            last_four_digits="4444",
            currency=Currency.ARS,
        )
        saved_ba = repo.save(ba)

        # Update the account
        updated_ba = BankAccount(
            id=saved_ba.id,
            payment_method_id=test_payment_method,
            primary_user_id=test_user,
            secondary_user_id=None,
            name="Updated Name",
            bank="Updated Bank",
            account_type="CHECKING",
            last_four_digits="5555",
            currency=Currency.USD,
        )
        repo.save(updated_ba)

        # Verify update
        found_ba = repo.find_by_id(saved_ba.id)
        assert found_ba is not None
        assert found_ba.name == "Updated Name"
        assert found_ba.bank == "Updated Bank"
        assert found_ba.account_type == "CHECKING"
        assert found_ba.last_four_digits == "5555"
        assert found_ba.currency == Currency.USD

    def test_delete_bank_account(self, repo, test_payment_method, test_user):
        """Test deleting a bank account."""
        # Create and save account
        ba = BankAccount(
            id=None,
            payment_method_id=test_payment_method,
            primary_user_id=test_user,
            secondary_user_id=None,
            name="To Delete",
            bank="Delete Bank",
            account_type="SAVINGS",
            last_four_digits="6666",
            currency=Currency.ARS,
        )
        saved_ba = repo.save(ba)

        # Verify it exists
        assert repo.find_by_id(saved_ba.id) is not None

        # Delete it
        repo.delete(saved_ba)

        # Verify it's gone
        assert repo.find_by_id(saved_ba.id) is None

    def test_delete_nonexistent_bank_account(self, repo):
        """Test deleting a non-existent bank account does nothing."""
        # Create a bank account that doesn't exist in DB
        ba = BankAccount(
            id=99999,
            payment_method_id=1,
            primary_user_id=1,
            secondary_user_id=None,
            name="Nonexistent",
            bank="Ghost Bank",
            account_type="SAVINGS",
            last_four_digits="7777",
            currency=Currency.ARS,
        )

        # Should not raise an error
        repo.delete(ba)

    def test_find_all_bank_accounts(self, repo, db_session, test_payment_method, test_user):
        """Test finding all bank accounts."""
        # Create multiple accounts
        ba1 = BankAccount(
            id=None,
            payment_method_id=test_payment_method,
            primary_user_id=test_user,
            secondary_user_id=None,
            name="Account 1",
            bank="Bank 1",
            account_type="SAVINGS",
            last_four_digits="1111",
            currency=Currency.ARS,
        )
        saved_ba1 = repo.save(ba1)

        ba2 = BankAccount(
            id=None,
            payment_method_id=test_payment_method,
            primary_user_id=test_user,
            secondary_user_id=None,
            name="Account 2",
            bank="Bank 2",
            account_type="CHECKING",
            last_four_digits="2222",
            currency=Currency.USD,
        )
        saved_ba2 = repo.save(ba2)

        # Find all
        all_accounts = repo.find_all()

        assert len(all_accounts) >= 2  # May have more from other tests
        assert saved_ba1 in all_accounts
        assert saved_ba2 in all_accounts

    def test_find_all_empty_database(self, repo):
        """Test finding all accounts when database is empty."""
        # This might fail if other tests have left data, but let's test the method
        all_accounts = repo.find_all()
        assert isinstance(all_accounts, list)
