import pytest
from datetime import datetime
from dataclasses import FrozenInstanceError

from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.domain.exceptions.domain_exceptions import PaymentMethodNameError


class TestPaymentMethod:
    """Test suite for PaymentMethod entity."""

    def test_creation_valid_with_id(self):
        """Test creating a valid PaymentMethod with an ID."""
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        pm = PaymentMethod(
            id=1,
            user_id=1,
            type=PaymentMethodType.CREDIT_CARD,
            name="Visa",
            is_active=True,
            created_at=created_at,
            updated_at=None,
        )
        assert pm.id == 1
        assert pm.user_id == 1
        assert pm.type == PaymentMethodType.CREDIT_CARD
        assert pm.name == "Visa"
        assert pm.is_active is True
        assert pm.created_at == created_at
        assert pm.updated_at is None

    def test_creation_valid_without_id(self):
        """Test creating a valid PaymentMethod without an ID."""
        pm = PaymentMethod(
            id=None,
            user_id=2,
            type=PaymentMethodType.CASH,
            name="Cash",
            is_active=False,
        )
        assert pm.id is None
        assert pm.user_id == 2
        assert pm.type == PaymentMethodType.CASH
        assert pm.name == "Cash"
        assert pm.is_active is False
        assert isinstance(pm.created_at, datetime)
        assert pm.updated_at is None

    def test_creation_invalid_name_empty(self):
        """Test that creating a PaymentMethod with empty name raises PaymentMethodNameError."""
        with pytest.raises(
            PaymentMethodNameError, match="Payment method name cannot be empty"
        ):
            PaymentMethod(id=1, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="")

    def test_creation_invalid_name_whitespace_only(self):
        """Test that creating a PaymentMethod with whitespace-only name raises PaymentMethodNameError."""
        with pytest.raises(
            PaymentMethodNameError, match="Payment method name cannot be empty"
        ):
            PaymentMethod(
                id=1, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="   "
            )

    def test_creation_invalid_name_none(self):
        """Test that creating a PaymentMethod with None name raises PaymentMethodNameError."""
        with pytest.raises(
            PaymentMethodNameError, match="Payment method name cannot be empty"
        ):
            PaymentMethod(
                id=1, user_id=1, type=PaymentMethodType.CREDIT_CARD, name=None
            )

    def test_creation_valid_name_with_spaces(self):
        """Test that creating a PaymentMethod with name containing spaces is valid."""
        pm = PaymentMethod(
            id=1, user_id=1, type=PaymentMethodType.BANK_ACCOUNT, name="Bank of America"
        )
        assert pm.name == "Bank of America"

    def test_equality_same_id(self):
        """Test equality when both PaymentMethods have the same ID."""
        pm1 = PaymentMethod(
            id=1, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        pm2 = PaymentMethod(
            id=1,
            user_id=2,  # different user_id
            type=PaymentMethodType.CASH,  # different type
            name="Cash",  # different name
        )
        assert pm1 == pm2

    def test_equality_different_id(self):
        """Test equality when PaymentMethods have different IDs."""
        pm1 = PaymentMethod(
            id=1, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        pm2 = PaymentMethod(
            id=2, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        assert pm1 != pm2

    def test_equality_none_id_different_instances(self):
        """Test equality when both PaymentMethods have None ID (different instances)."""
        pm1 = PaymentMethod(
            id=None, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        pm2 = PaymentMethod(
            id=None, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        assert pm1 != pm2  # Different object identities

    def test_equality_none_id_same_instance(self):
        """Test equality when comparing the same instance with None ID."""
        pm = PaymentMethod(
            id=None, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        assert pm == pm  # Same instance

    def test_equality_different_types(self):
        """Test equality when comparing PaymentMethod with non-PaymentMethod object."""
        pm = PaymentMethod(
            id=1, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        assert pm != "not a payment method"
        assert pm != 123

    def test_hash_with_id(self):
        """Test hash consistency when PaymentMethod has an ID."""
        pm1 = PaymentMethod(
            id=1, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        pm2 = PaymentMethod(id=1, user_id=2, type=PaymentMethodType.CASH, name="Cash")
        assert hash(pm1) == hash(pm2)
        assert hash(pm1) == hash(1)  # Should hash to the ID

    def test_hash_none_id(self):
        """Test hash when PaymentMethod has None ID."""
        pm1 = PaymentMethod(
            id=None, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        pm2 = PaymentMethod(
            id=None, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        # Different instances should have different hashes based on id(self)
        assert hash(pm1) != hash(pm2)
        assert hash(pm1) == hash(id(pm1))
        assert hash(pm2) == hash(id(pm2))

    def test_frozen_instance_cannot_modify(self):
        """Test that PaymentMethod is frozen and cannot be modified after creation."""
        pm = PaymentMethod(
            id=1, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        with pytest.raises(FrozenInstanceError):
            pm.name = "Mastercard"
        with pytest.raises(FrozenInstanceError):
            pm.is_active = False
        with pytest.raises(FrozenInstanceError):
            pm.user_id = 2

    def test_all_payment_method_types(self):
        """Test creating PaymentMethod with all possible PaymentMethodType values."""
        for pm_type in PaymentMethodType:
            pm = PaymentMethod(
                id=1, user_id=1, type=pm_type, name=f"Test {pm_type.value}"
            )
            assert pm.type == pm_type

    def test_created_at_defaults_to_now(self):
        """Test that created_at defaults to current datetime if not provided."""
        before = datetime.now()
        pm = PaymentMethod(
            id=1, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        after = datetime.now()
        assert before <= pm.created_at <= after

    def test_updated_at_defaults_to_none(self):
        """Test that updated_at defaults to None."""
        pm = PaymentMethod(
            id=1, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"
        )
        assert pm.updated_at is None

    def test_custom_updated_at(self):
        """Test setting a custom updated_at value."""
        updated_at = datetime(2023, 12, 31, 23, 59, 59)
        pm = PaymentMethod(
            id=1,
            user_id=1,
            type=PaymentMethodType.CREDIT_CARD,
            name="Visa",
            updated_at=updated_at,
        )
        assert pm.updated_at == updated_at
