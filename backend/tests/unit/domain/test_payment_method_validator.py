import pytest

from app.domain.entities.payment_method import PaymentMethod
from app.domain.services.payment_method_validator import PaymentMethodValidator
from app.domain.exceptions.domain_exceptions import PaymentMethodInstallmentsError
from app.domain.value_objects.payment_method_type import PaymentMethodType


class TestPaymentMethodValidator:
    """Unit tests for PaymentMethodValidator service."""

    def test_validate_installments_credit_card_multiple_installments_allowed(self):
        """Test that credit cards can have multiple installments."""
        # Arrange
        payment_method = PaymentMethod(
            id=1,
            user_id=1,
            type=PaymentMethodType.CREDIT_CARD,
            name="Visa Gold"
        )

        # Act & Assert
        result = PaymentMethodValidator.validate_installments(payment_method, 3)
        assert result is True

        result = PaymentMethodValidator.validate_installments(payment_method, 12)
        assert result is True

    def test_validate_installments_credit_card_single_installment_allowed(self):
        """Test that credit cards can have single installment."""
        # Arrange
        payment_method = PaymentMethod(
            id=1,
            user_id=1,
            type=PaymentMethodType.CREDIT_CARD,
            name="Mastercard"
        )

        # Act & Assert
        result = PaymentMethodValidator.validate_installments(payment_method, 1)
        assert result is True

    def test_validate_installments_cash_multiple_installments_not_allowed(self):
        """Test that cash payments cannot have multiple installments."""
        # Arrange
        payment_method = PaymentMethod(
            id=2,
            user_id=1,
            type=PaymentMethodType.CASH,
            name="Cash"
        )

        # Act & Assert
        result = PaymentMethodValidator.validate_installments(payment_method, 3)
        assert result is False

    def test_validate_installments_bank_account_multiple_installments_not_allowed(self):
        """Test that bank account payments cannot have multiple installments."""
        # Arrange
        payment_method = PaymentMethod(
            id=3,
            user_id=1,
            type=PaymentMethodType.BANK_ACCOUNT,
            name="Checking Account"
        )

        # Act & Assert
        result = PaymentMethodValidator.validate_installments(payment_method, 6)
        assert result is False

    def test_validate_installments_digital_wallet_multiple_installments_not_allowed(self):
        """Test that digital wallet payments cannot have multiple installments."""
        # Arrange
        payment_method = PaymentMethod(
            id=4,
            user_id=1,
            type=PaymentMethodType.DIGITAL_WALLET,
            name="PayPal"
        )

        # Act & Assert
        result = PaymentMethodValidator.validate_installments(payment_method, 2)
        assert result is False

    def test_validate_installments_non_credit_card_single_installment_allowed(self):
        """Test that non-credit card payment methods can have single installment."""
        # Arrange - Test all non-credit card types
        payment_methods = [
            PaymentMethod(id=5, user_id=1, type=PaymentMethodType.CASH, name="Cash"),
            PaymentMethod(id=6, user_id=1, type=PaymentMethodType.BANK_ACCOUNT, name="Bank"),
            PaymentMethod(id=7, user_id=1, type=PaymentMethodType.DIGITAL_WALLET, name="Wallet"),
        ]

        # Act & Assert
        for payment_method in payment_methods:
            result = PaymentMethodValidator.validate_installments(payment_method, 1)
            assert result is True

    def test_validate_installments_zero_installments_allowed_for_all_types(self):
        """Test that zero installments are allowed for all payment method types."""
        # Arrange
        payment_methods = [
            PaymentMethod(id=8, user_id=1, type=PaymentMethodType.CREDIT_CARD, name="Visa"),
            PaymentMethod(id=9, user_id=1, type=PaymentMethodType.CASH, name="Cash"),
            PaymentMethod(id=10, user_id=1, type=PaymentMethodType.BANK_ACCOUNT, name="Bank"),
            PaymentMethod(id=11, user_id=1, type=PaymentMethodType.DIGITAL_WALLET, name="Wallet"),
        ]

        # Act & Assert
        for payment_method in payment_methods:
            result = PaymentMethodValidator.validate_installments(payment_method, 0)
            assert result is True

    def test_validate_installments_negative_installments_allowed(self):
        """Test that negative installments are allowed (no validation for negative values)."""
        # Arrange
        payment_method = PaymentMethod(
            id=12,
            user_id=1,
            type=PaymentMethodType.CASH,
            name="Cash"
        )

        # Act & Assert - Negative values don't trigger the multiple installments check
        result = PaymentMethodValidator.validate_installments(payment_method, -1)
        assert result is True

    def test_validate_installments_boundary_values(self):
        """Test boundary values around the installments threshold."""
        # Arrange
        credit_card = PaymentMethod(
            id=13,
            user_id=1,
            type=PaymentMethodType.CREDIT_CARD,
            name="Visa"
        )

        cash = PaymentMethod(
            id=14,
            user_id=1,
            type=PaymentMethodType.CASH,
            name="Cash"
        )

        # Act & Assert
        # Credit card should allow 2 installments (boundary)
        result = PaymentMethodValidator.validate_installments(credit_card, 2)
        assert result is True

        # Cash should reject 2 installments (boundary)
        result = PaymentMethodValidator.validate_installments(cash, 2)
        assert result is False

    def test_validate_installments_large_installment_numbers(self):
        """Test validation with large installment numbers."""
        # Arrange
        credit_card = PaymentMethod(
            id=15,
            user_id=1,
            type=PaymentMethodType.CREDIT_CARD,
            name="Premium Card"
        )

        cash = PaymentMethod(
            id=16,
            user_id=1,
            type=PaymentMethodType.CASH,
            name="Cash"
        )

        # Act & Assert
        # Credit card should allow large numbers
        result = PaymentMethodValidator.validate_installments(credit_card, 60)
        assert result is True

        # Cash should reject large numbers
        result = PaymentMethodValidator.validate_installments(cash, 60)
        assert result is False

    def test_validate_installments_all_payment_method_types(self):
        """Test validation across all payment method types with multiple installments."""
        # Arrange
        payment_methods = [
            (PaymentMethodType.CREDIT_CARD, True),  # Should allow
            (PaymentMethodType.CASH, False),        # Should reject
            (PaymentMethodType.BANK_ACCOUNT, False), # Should reject
            (PaymentMethodType.DIGITAL_WALLET, False), # Should reject
        ]

        # Act & Assert
        for pm_type, should_allow in payment_methods:
            payment_method = PaymentMethod(
                id=17,
                user_id=1,
                type=pm_type,
                name=f"Test {pm_type.value}"
            )

            if should_allow:
                result = PaymentMethodValidator.validate_installments(payment_method, 3)
                assert result is True
            else:
                result = PaymentMethodValidator.validate_installments(payment_method, 3)
                assert result is False