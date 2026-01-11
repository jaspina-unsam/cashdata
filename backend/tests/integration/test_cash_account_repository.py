import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

from app.domain.entities.cash_account import CashAccount
from app.domain.value_objects.money import Currency
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.models.cash_account_model import CashAccountModel
from app.infrastructure.persistence.models.payment_method_model import PaymentMethodModel
from app.infrastructure.persistence.repositories.sqlalchemy_cash_account_repository import (
    SQLAlchemyCashAccountRepository,
)


@pytest.fixture
def db_session():
    """In-memory SQLite for tests"""
    engine = create_engine("sqlite:///:memory:")
    UserModel.metadata.create_all(engine)
    PaymentMethodModel.metadata.create_all(engine)
    CashAccountModel.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create test user
    test_user = UserModel(
        id=1,
        name="Test User",
        email="test@example.com",
        wage_amount=50000,
        wage_currency="ARS",
        is_deleted=False,
    )
    session.add(test_user)

    # Create test payment methods
    payment_method1 = PaymentMethodModel(
        id=1,
        user_id=1,
        type="cash",
        name="Test Payment Method 1",
        is_active=True,
        created_at=datetime.now(),
    )
    payment_method2 = PaymentMethodModel(
        id=2,
        user_id=1,
        type="cash",
        name="Test Payment Method 2",
        is_active=True,
        created_at=datetime.now(),
    )
    payment_method3 = PaymentMethodModel(
        id=3,
        user_id=1,
        type="cash",
        name="Test Payment Method 3",
        is_active=True,
        created_at=datetime.now(),
    )
    payment_method4 = PaymentMethodModel(
        id=4,
        user_id=1,
        type="cash",
        name="Test Payment Method 4",
        is_active=True,
        created_at=datetime.now(),
    )
    session.add_all([test_user, payment_method1, payment_method2, payment_method3, payment_method4])
    session.commit()

    yield session
    session.close()


@pytest.fixture
def cash_account_repository(db_session: Session):
    return SQLAlchemyCashAccountRepository(db_session)


class TestSQLAlchemyCashAccountRepositorySave:
    def test_should_save_new_cash_account(self, cash_account_repository):
        # Arrange
        new_account = CashAccount(
            id=None,
            payment_method_id=1,
            user_id=1,
            name="Main Cash Account",
            currency=Currency.ARS,
        )

        # Act
        saved_account = cash_account_repository.save(new_account)

        # Assert
        assert saved_account.id is not None
        assert saved_account.user_id == 1
        assert saved_account.payment_method_id == 1
        assert saved_account.name == "Main Cash Account"
        assert saved_account.currency == Currency.ARS

        # Verify in DB
        retrieved = cash_account_repository.find_by_id(saved_account.id)
        assert retrieved == saved_account

    def test_should_update_existing_cash_account(self, cash_account_repository):
        # Arrange - Create and save
        account = CashAccount(
            id=None,
            payment_method_id=2,
            user_id=1,
            name="Savings Account",
            currency=Currency.ARS,
        )
        saved = cash_account_repository.save(account)
        original_id = saved.id

        # Act - Update
        updated_account = CashAccount(
            id=original_id,
            payment_method_id=2,
            user_id=1,
            name="Updated Savings Account",
            currency=Currency.USD,
        )
        updated = cash_account_repository.save(updated_account)

        # Assert
        assert updated.id == original_id
        assert updated.name == "Updated Savings Account"
        assert updated.currency == Currency.USD

        # Verify in DB
        from_db = cash_account_repository.find_by_id(original_id)
        assert from_db.name == "Updated Savings Account"
        assert from_db.currency == Currency.USD


class TestSQLAlchemyCashAccountRepositoryFindById:
    def test_should_find_existing_cash_account(self, cash_account_repository):
        # Arrange
        account = CashAccount(
            id=None,
            payment_method_id=1,
            user_id=1,
            name="Checking Account",
            currency=Currency.ARS,
        )
        saved = cash_account_repository.save(account)

        # Act
        found = cash_account_repository.find_by_id(saved.id)

        # Assert
        assert found is not None
        assert found.id == saved.id
        assert found.name == "Checking Account"

    def test_should_return_none_for_nonexistent_id(self, cash_account_repository):
        # Act
        found = cash_account_repository.find_by_id(999)

        # Assert
        assert found is None


class TestSQLAlchemyCashAccountRepositoryFindByUserId:
    def test_should_return_all_accounts_for_user(self, cash_account_repository):
        # Arrange
        account1 = CashAccount(
            id=None,
            payment_method_id=1,
            user_id=1,
            name="Account 1",
            currency=Currency.ARS,
        )
        account2 = CashAccount(
            id=None,
            payment_method_id=2,
            user_id=1,
            name="Account 2",
            currency=Currency.USD,
        )
        account3 = CashAccount(
            id=None,
            payment_method_id=3,
            user_id=1,
            name="Account 3",
            currency=Currency.ARS,
        )

        cash_account_repository.save(account1)
        cash_account_repository.save(account2)
        cash_account_repository.save(account3)

        # Act
        user_accounts = cash_account_repository.find_by_user_id(1)

        # Assert
        assert len(user_accounts) == 3
        names = [a.name for a in user_accounts]
        assert "Account 1" in names
        assert "Account 2" in names
        assert "Account 3" in names

    def test_should_return_empty_list_for_user_without_accounts(
        self, cash_account_repository
    ):
        # Act
        user_accounts = cash_account_repository.find_by_user_id(999)

        # Assert
        assert user_accounts == []


class TestSQLAlchemyCashAccountRepositoryDelete:
    def test_should_delete_existing_cash_account(self, cash_account_repository):
        # Arrange
        account = CashAccount(
            id=None,
            payment_method_id=1,
            user_id=1,
            name="Account to Delete",
            currency=Currency.ARS,
        )
        saved = cash_account_repository.save(account)
        account_id = saved.id

        # Verify it exists
        assert cash_account_repository.find_by_id(account_id) is not None

        # Act
        cash_account_repository.delete(saved)

        # Assert
        assert cash_account_repository.find_by_id(account_id) is None


class TestSQLAlchemyCashAccountRepositoryExistsByPaymentMethodId:
    def test_should_return_true_when_account_exists_for_payment_method(self, cash_account_repository):
        # Arrange
        account = CashAccount(
            id=None,
            payment_method_id=4,
            user_id=1,
            name="Account for PM 4",
            currency=Currency.ARS,
        )
        cash_account_repository.save(account)

        # Act
        exists = cash_account_repository.exists_by_payment_method_id(4)

        # Assert
        assert exists is True

    def test_should_return_false_when_no_account_exists_for_payment_method(self, cash_account_repository):
        # Act
        exists = cash_account_repository.exists_by_payment_method_id(999)

        # Assert
        assert exists is False