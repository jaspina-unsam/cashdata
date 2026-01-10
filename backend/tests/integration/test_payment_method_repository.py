import pytest
from datetime import datetime
from decimal import Decimal

from app.domain.entities.payment_method import PaymentMethod
from app.domain.entities.user import User
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.domain.value_objects.money import Money, Currency
from app.infrastructure.persistence.mappers.user_mapper import UserMapper
from app.infrastructure.persistence.repositories.sqlalchemy_payment_method_repository import (
    SQLAlchemyPaymentMethodRepository,
)


class TestSQLAlchemyPaymentMethodRepository:
    """Integration tests for SQLAlchemyPaymentMethodRepository."""

    def test_find_by_id_existing_payment_method(self, db_session):
        """Test finding an existing payment method by ID."""
        # Create a user first
        user = User(
            id=None,
            email="test_find_by_id@example.com",
            name="Test User",
            wage=Money(Decimal("1000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user_model = UserMapper.to_model(user)
        db_session.add(user_model)
        db_session.flush()
        user_id = user_model.id

        # Create and save a payment method
        pm = PaymentMethod(
            id=None, user_id=user_id, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        repo = SQLAlchemyPaymentMethodRepository(db_session)
        saved_pm = repo.save(pm)

        # Find the payment method
        found_pm = repo.find_by_id(saved_pm.id)

        assert found_pm is not None
        assert found_pm == saved_pm
        assert found_pm.id == saved_pm.id
        assert found_pm.user_id == user_id
        assert found_pm.type == PaymentMethodType.CREDIT_CARD
        assert found_pm.name == "Visa"
        assert found_pm.is_active is True

    def test_find_by_id_non_existing_payment_method(self, db_session):
        """Test finding a non-existing payment method by ID returns None."""
        repo = SQLAlchemyPaymentMethodRepository(db_session)
        found_pm = repo.find_by_id(99999)
        assert found_pm is None

    def test_find_by_user_id_all_payment_methods(self, db_session):
        """Test finding all payment methods for a user."""
        # Create a user
        user = User(
            id=None,
            email="test_find_by_user@example.com",
            name="Test User",
            wage=Money(Decimal("1000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user_model = UserMapper.to_model(user)
        db_session.add(user_model)
        db_session.flush()
        user_id = user_model.id

        # Create multiple payment methods
        pm1 = PaymentMethod(
            id=None, user_id=user_id, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        pm2 = PaymentMethod(
            id=None, user_id=user_id, type=PaymentMethodType.CASH, name="Cash"
        )
        pm3 = PaymentMethod(
            id=None, user_id=user_id, type=PaymentMethodType.BANK_ACCOUNT, name="Bank"
        )

        repo = SQLAlchemyPaymentMethodRepository(db_session)
        repo.save(pm1)
        repo.save(pm2)
        repo.save(pm3)

        # Find all payment methods for the user
        found_pms = repo.find_by_user_id(user_id)

        assert len(found_pms) == 3
        pm_names = {pm.name for pm in found_pms}
        assert pm_names == {"Visa", "Cash", "Bank"}

    def test_find_by_user_id_with_type_filter(self, db_session):
        """Test finding payment methods for a user filtered by type."""
        # Create a user
        user = User(
            id=None,
            email="test_find_by_user_type@example.com",
            name="Test User",
            wage=Money(Decimal("1000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user_model = UserMapper.to_model(user)
        db_session.add(user_model)
        db_session.flush()
        user_id = user_model.id

        # Create payment methods of different types
        pm1 = PaymentMethod(
            id=None, user_id=user_id, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        pm2 = PaymentMethod(
            id=None,
            user_id=user_id,
            type=PaymentMethodType.CREDIT_CARD,
            name="Mastercard",
        )
        pm3 = PaymentMethod(
            id=None, user_id=user_id, type=PaymentMethodType.CASH, name="Cash"
        )

        repo = SQLAlchemyPaymentMethodRepository(db_session)
        repo.save(pm1)
        repo.save(pm2)
        repo.save(pm3)

        # Find only credit card payment methods
        found_pms = repo.find_by_user_id(user_id, PaymentMethodType.CREDIT_CARD)

        assert len(found_pms) == 2
        for pm in found_pms:
            assert pm.type == PaymentMethodType.CREDIT_CARD
        pm_names = {pm.name for pm in found_pms}
        assert pm_names == {"Visa", "Mastercard"}

    def test_find_by_user_id_no_payment_methods(self, db_session):
        """Test finding payment methods for a user with no payment methods."""
        # Create a user
        user = User(
            id=None,
            email="test_no_pms@example.com",
            name="Test User",
            wage=Money(Decimal("1000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user_model = UserMapper.to_model(user)
        db_session.add(user_model)
        db_session.flush()
        user_id = user_model.id

        repo = SQLAlchemyPaymentMethodRepository(db_session)
        found_pms = repo.find_by_user_id(user_id)

        assert found_pms == []

    def test_find_by_user_id_different_users(self, db_session):
        """Test that payment methods are isolated between users."""
        # Create two users
        user1 = User(
            id=None,
            email="user1@example.com",
            name="User 1",
            wage=Money(Decimal("1000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user2 = User(
            id=None,
            email="user2@example.com",
            name="User 2",
            wage=Money(Decimal("1000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user1_model = UserMapper.to_model(user1)
        user2_model = UserMapper.to_model(user2)
        db_session.add(user1_model)
        db_session.add(user2_model)
        db_session.flush()
        user1_id = user1_model.id
        user2_id = user2_model.id

        # Create payment methods for each user
        pm1 = PaymentMethod(
            id=None, user_id=user1_id, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        pm2 = PaymentMethod(
            id=None, user_id=user2_id, type=PaymentMethodType.CASH, name="Cash"
        )

        repo = SQLAlchemyPaymentMethodRepository(db_session)
        repo.save(pm1)
        repo.save(pm2)

        # Check user1's payment methods
        user1_pms = repo.find_by_user_id(user1_id)
        assert len(user1_pms) == 1
        assert user1_pms[0].name == "Visa"

        # Check user2's payment methods
        user2_pms = repo.find_by_user_id(user2_id)
        assert len(user2_pms) == 1
        assert user2_pms[0].name == "Cash"

    def test_save_insert_new_payment_method(self, db_session):
        """Test saving a new payment method (insert)."""
        # Create a user
        user = User(
            id=None,
            email="test_save_insert@example.com",
            name="Test User",
            wage=Money(Decimal("1000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user_model = UserMapper.to_model(user)
        db_session.add(user_model)
        db_session.flush()
        user_id = user_model.id

        # Create a new payment method
        pm = PaymentMethod(
            id=None,
            user_id=user_id,
            type=PaymentMethodType.DIGITAL_WALLET,
            name="PayPal",
            is_active=False,
        )

        repo = SQLAlchemyPaymentMethodRepository(db_session)
        saved_pm = repo.save(pm)

        assert saved_pm.id is not None
        assert saved_pm.user_id == user_id
        assert saved_pm.type == PaymentMethodType.DIGITAL_WALLET
        assert saved_pm.name == "PayPal"
        assert saved_pm.is_active is False
        assert saved_pm.created_at is not None
        assert saved_pm.updated_at is None

        # Verify it can be found
        found_pm = repo.find_by_id(saved_pm.id)
        assert found_pm == saved_pm

    def test_save_update_existing_payment_method(self, db_session):
        """Test saving an existing payment method (update)."""
        # Create a user
        user = User(
            id=None,
            email="test_save_update@example.com",
            name="Test User",
            wage=Money(Decimal("1000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user_model = UserMapper.to_model(user)
        db_session.add(user_model)
        db_session.flush()
        user_id = user_model.id

        # Create and save initial payment method
        pm = PaymentMethod(
            id=None,
            user_id=user_id,
            type=PaymentMethodType.BANK_ACCOUNT,
            name="Bank Account",
        )
        repo = SQLAlchemyPaymentMethodRepository(db_session)
        saved_pm = repo.save(pm)

        # Update the payment method
        updated_pm = PaymentMethod(
            id=saved_pm.id,
            user_id=saved_pm.user_id,
            type=saved_pm.type,
            name="Updated Bank Account",
            is_active=False,
            created_at=saved_pm.created_at,
            updated_at=datetime.now(),
        )
        updated_saved_pm = repo.save(updated_pm)

        assert updated_saved_pm.id == saved_pm.id
        assert updated_saved_pm.name == "Updated Bank Account"
        assert updated_saved_pm.is_active is False
        assert updated_saved_pm.updated_at is not None

        # Verify the update in database
        found_pm = repo.find_by_id(saved_pm.id)
        assert found_pm.name == "Updated Bank Account"
        assert found_pm.is_active is False

    def test_save_update_non_existing_payment_method(self, db_session):
        """Test saving an update for a non-existing payment method creates new one."""
        # Create a user
        user = User(
            id=None,
            email="test_save_update_nonexist@example.com",
            name="Test User",
            wage=Money(Decimal("1000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user_model = UserMapper.to_model(user)
        db_session.add(user_model)
        db_session.flush()
        user_id = user_model.id

        # Try to update a non-existing payment method
        pm = PaymentMethod(
            id=99999,  # Non-existing ID
            user_id=user_id,
            type=PaymentMethodType.CASH,
            name="Cash",
        )

        repo = SQLAlchemyPaymentMethodRepository(db_session)
        saved_pm = repo.save(pm)

        # Should create a new one with new ID
        assert saved_pm.id != 99999
        assert saved_pm.id is not None
        assert saved_pm.user_id == user_id
        assert saved_pm.name == "Cash"

    def test_delete_existing_payment_method(self, db_session):
        """Test deleting an existing payment method."""
        # Create a user
        user = User(
            id=None,
            email="test_delete@example.com",
            name="Test User",
            wage=Money(Decimal("1000"), Currency.ARS),
            is_deleted=False,
            deleted_at=None,
        )
        user_model = UserMapper.to_model(user)
        db_session.add(user_model)
        db_session.flush()
        user_id = user_model.id

        # Create and save a payment method
        pm = PaymentMethod(
            id=None, user_id=user_id, type=PaymentMethodType.CREDIT_CARD, name="Amex"
        )
        repo = SQLAlchemyPaymentMethodRepository(db_session)
        saved_pm = repo.save(pm)

        # Delete the payment method
        repo.delete(saved_pm.id)

        # Verify it's deleted
        found_pm = repo.find_by_id(saved_pm.id)
        assert found_pm is None

    def test_delete_non_existing_payment_method(self, db_session):
        """Test deleting a non-existing payment method does not raise error."""
        repo = SQLAlchemyPaymentMethodRepository(db_session)
        # Should not raise any exception
        repo.delete(99999)
