import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from cashdata.domain.entities.user import User
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.infrastructure.persistence.models.user_model import UserModel
from cashdata.infrastructure.persistence.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from decimal import Decimal


@pytest.fixture
def db_session():
    """In-memory SQLite for tests"""
    engine = create_engine("sqlite:///:memory:")
    UserModel.metadata.create_all(engine)  # Create tables
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def make_user():
    def _make(id, name, email, wage_amount, wage_currency=Currency.ARS):
        return User(
            id=id,
            name=name,
            email=email,
            wage=Money(Decimal(str(wage_amount)), wage_currency),
        )

    return _make


@pytest.fixture
def user_repository(db_session: Session):
    return SQLAlchemyUserRepository(db_session)


class TestSQLAlchemyUserRepositorySave:
    def test_should_save_new_user(self, user_repository, make_user):
        # Arrange
        new_user = make_user(None, "John Doe", "john@example.com", 50000)

        # Act
        saved_user = user_repository.save(new_user)

        # Assert
        assert saved_user.id is not None
        assert saved_user.name == "John Doe"
        assert saved_user.email == "john@example.com"
        assert saved_user.wage.amount == Decimal("50000")
        assert saved_user.wage.currency == Currency.ARS

        # Verify in DB
        retrieved = user_repository.find_by_id(saved_user.id)
        assert retrieved == saved_user

    def test_should_update_existing_user(self, user_repository, make_user):
        """
        Given: A user exists in DB
        When: I modify the user and save again
        Then: The changes should persist
        """
        # 1. Crear y guardar usuario
        user = make_user(None, "John", "john@example.com", 5000)
        saved = user_repository.save(user)
        original_id = saved.id

        # 2. Modificar y guardar de nuevo
        saved.update_wage(Money(Decimal("6000"), Currency.ARS))
        updated = user_repository.save(saved)

        # 3. Verificar que se actualizó (mismo ID)
        assert updated.id == original_id
        assert updated.wage.amount == Decimal("6000")

        # 4. Verificar en DB
        from_db = user_repository.find_by_id(original_id)
        assert from_db.wage.amount == Decimal("6000")

    def test_should_save_user_with_different_currency(self, user_repository, make_user):
        """
        Given: A user with USD wage
        When: I save the user
        Then: Currency should be preserved
        """
        user = make_user(None, "Jane", "jane@example.com", 3000, Currency.USD)
        saved = user_repository.save(user)

        retrieved = user_repository.find_by_id(saved.id)
        assert retrieved.wage.currency == Currency.USD

    def test_should_handle_duplicate_email(self, user_repository, make_user):
        """
        Given: A user with email "john@example.com" exists
        When: I try to save another user with the same email
        Then: Should raise an exception (unique constraint)
        """
        user1 = make_user(None, "John", "john@example.com", 5000)
        user_repository.save(user1)

        user2 = make_user(None, "Jane", "john@example.com", 6000)

        with pytest.raises(Exception):  # SQLAlchemy raises IntegrityError
            user_repository.save(user2)
            user_repository.session.commit()  # Force constraint check


class TestSQLAlchemyUserRepositoryFind:
    def test_should_find_user_by_id(self, user_repository, make_user):
        """
        Given: A user exists in DB
        When: I search by ID
        Then: Should return the correct user
        """
        user = make_user(None, "John", "john@example.com", 5000)
        saved = user_repository.save(user)

        found = user_repository.find_by_id(saved.id)

        assert found is not None
        assert found.id == saved.id
        assert found.name == "John"
        assert found.email == "john@example.com"

    def test_should_return_none_when_user_not_found(self, user_repository):
        """
        Given: No users in DB
        When: I search for ID 999
        Then: Should return None
        """
        result = user_repository.find_by_id(999)
        assert result is None

    def test_should_find_all_users(self, user_repository, make_user):
        """
        Given: Multiple users in DB
        When: I call find_all()
        Then: Should return all users
        """
        user1 = make_user(None, "John", "john@example.com", 5000)
        user2 = make_user(None, "Jane", "jane@example.com", 6000)
        user3 = make_user(None, "Bob", "bob@example.com", 7000)

        user_repository.save(user1)
        user_repository.save(user2)
        user_repository.save(user3)

        all_users = user_repository.find_all()

        assert len(all_users) == 3
        assert all(isinstance(u, User) for u in all_users)

    def test_should_return_empty_list_when_no_users(self, user_repository):
        """
        Given: No users in DB
        When: I call find_all()
        Then: Should return empty list
        """
        result = user_repository.find_all()
        assert result == []

    def test_should_map_money_correctly(self, user_repository, make_user):
        """
        Given: A user saved with Money(2540, USD)
        When: I retrieve the user
        Then: wage should be Money object with correct amount and currency
        """
        user = make_user(None, "John", "john@example.com", 2540, Currency.USD)
        saved = user_repository.save(user)

        retrieved = user_repository.find_by_id(saved.id)

        assert isinstance(retrieved.wage, Money)
        assert retrieved.wage.amount == Decimal("2540")
        assert retrieved.wage.currency == Currency.USD


class TestSQLAlchemyUserRepositoryDelete:
    def test_should_delete_existing_user(self, user_repository, make_user):
        """
        Given: A user exists in DB
        When: I delete the user
        Then: The user should no longer exist
        """
        user = make_user(None, "John", "john@example.com", 5000)
        saved = user_repository.save(user)
        user_id = saved.id

        # Delete
        result = user_repository.delete(user_id)

        assert result is True

        # Verify deleted
        found = user_repository.find_by_id(user_id)
        assert found is None

    def test_should_return_false_when_deleting_nonexistent_user(self, user_repository):
        """
        Given: No user with ID 999
        When: I try to delete ID 999
        Then: Should return False
        """
        result = user_repository.delete(999)
        assert result is False
