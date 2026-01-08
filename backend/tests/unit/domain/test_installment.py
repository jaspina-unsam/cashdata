import pytest
from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

from app.domain.entities.installment import Installment
from app.domain.value_objects.money import Money, Currency


class TestInstallmentEntity:
    """Unit tests for Installment domain entity"""

    # ===== HAPPY PATH =====

    def test_create_installment_with_all_fields(self):
        """
        GIVEN: Valid installment data with all fields
        WHEN: Creating an Installment
        THEN: Entity is created successfully
        """
        # Arrange & Act
        installment = Installment(
            id=1,
            purchase_id=100,
            installment_number=3,
            total_installments=6,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202501",
        )

        # Assert
        assert installment.id == 1
        assert installment.purchase_id == 100
        assert installment.installment_number == 3
        assert installment.total_installments == 6
        assert installment.amount.amount == Decimal("5000.00")
        assert installment.amount.currency == Currency.ARS
        assert installment.billing_period == "202501"

    def test_create_installment_without_id(self):
        """
        GIVEN: Installment data without ID (new entity)
        WHEN: Creating an Installment
        THEN: ID should be None
        """
        # Arrange & Act
        installment = Installment(
            id=None,
            purchase_id=100,
            installment_number=1,
            total_installments=1,
            amount=Money(Decimal("10000.00"), Currency.ARS),
            billing_period="202502",
        )

        # Assert
        assert installment.id is None

    def test_create_first_installment(self):
        """
        GIVEN: First installment of a multi-installment purchase
        WHEN: Creating an Installment
        THEN: installment_number should be 1
        """
        # Arrange & Act
        installment = Installment(
            id=1,
            purchase_id=100,
            installment_number=1,
            total_installments=12,
            amount=Money(Decimal("8333.33"), Currency.ARS),
            billing_period="202501",
        )

        # Assert
        assert installment.installment_number == 1
        assert installment.total_installments == 12

    def test_create_last_installment(self):
        """
        GIVEN: Last installment of a multi-installment purchase
        WHEN: Creating an Installment
        THEN: installment_number should equal total_installments
        """
        # Arrange & Act
        installment = Installment(
            id=1,
            purchase_id=100,
            installment_number=12,
            total_installments=12,
            amount=Money(Decimal("8333.33"), Currency.ARS),
            billing_period="202612",
        )

        # Assert
        assert installment.installment_number == 12
        assert installment.installment_number == installment.total_installments

    def test_create_single_installment(self):
        """
        GIVEN: Single payment (1/1)
        WHEN: Creating an Installment
        THEN: Both numbers should be 1
        """
        # Arrange & Act
        installment = Installment(
            id=1,
            purchase_id=100,
            installment_number=1,
            total_installments=1,
            amount=Money(Decimal("50000.00"), Currency.ARS),
            billing_period="202501",
        )

        # Assert
        assert installment.installment_number == 1
        assert installment.total_installments == 1

    def test_create_installment_with_usd(self):
        """
        GIVEN: Installment with USD currency
        WHEN: Creating an Installment
        THEN: Currency is preserved
        """
        # Arrange & Act
        installment = Installment(
            id=1,
            purchase_id=100,
            installment_number=1,
            total_installments=3,
            amount=Money(Decimal("100.00"), Currency.USD),
            billing_period="202501",
        )

        # Assert
        assert installment.amount.currency == Currency.USD

    # ===== VALIDATION ERRORS - INSTALLMENT NUMBERS =====

    def test_raises_error_for_zero_installment_number(self):
        """
        GIVEN: installment_number = 0
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="installment_number must be >= 1"):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=0,
                total_installments=6,
                amount=Money(Decimal("5000.00"), Currency.ARS),
                billing_period="202501",
            )

    def test_raises_error_for_negative_installment_number(self):
        """
        GIVEN: installment_number < 0
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="installment_number must be >= 1"):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=-1,
                total_installments=6,
                amount=Money(Decimal("5000.00"), Currency.ARS),
                billing_period="202501",
            )

    def test_raises_error_for_zero_total_installments(self):
        """
        GIVEN: total_installments = 0
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="total_installments must be >= 1"):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=1,
                total_installments=0,
                amount=Money(Decimal("5000.00"), Currency.ARS),
                billing_period="202501",
            )

    def test_raises_error_for_negative_total_installments(self):
        """
        GIVEN: total_installments < 0
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="total_installments must be >= 1"):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=1,
                total_installments=-5,
                amount=Money(Decimal("5000.00"), Currency.ARS),
                billing_period="202501",
            )

    def test_raises_error_when_installment_number_exceeds_total(self):
        """
        GIVEN: installment_number > total_installments
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError,
            match="installment_number \\(7\\) cannot exceed total_installments \\(6\\)",
        ):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=7,
                total_installments=6,
                amount=Money(Decimal("5000.00"), Currency.ARS),
                billing_period="202501",
            )

    # ===== VALIDATION ERRORS - AMOUNT =====

    def test_raises_error_for_zero_amount(self):
        """
        GIVEN: amount = 0
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="amount cannot be zero"):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=1,
                total_installments=6,
                amount=Money(Decimal("0.00"), Currency.ARS),
                billing_period="202501",
            )

    def test_allows_negative_amount_for_credits(self):
        """
        GIVEN: amount < 0 (credit/bonification)
        WHEN: Creating an Installment
        THEN: Should succeed
        """
        # Arrange & Act
        installment = Installment(
            id=None,
            purchase_id=100,
            installment_number=1,
            total_installments=1,
            amount=Money(Decimal("-100.00"), Currency.ARS),
            billing_period="202501",
        )

        # Assert
        assert installment.amount.amount == Decimal("-100.00")

    # ===== VALIDATION ERRORS - BILLING PERIOD =====

    def test_raises_error_for_invalid_billing_period_format(self):
        """
        GIVEN: billing_period not in YYYYMM format
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="billing_period must be in YYYYMM format"):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=1,
                total_installments=6,
                amount=Money(Decimal("5000.00"), Currency.ARS),
                billing_period="2025-01",
            )

    def test_raises_error_for_billing_period_too_short(self):
        """
        GIVEN: billing_period with less than 6 digits
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="billing_period must be in YYYYMM format"):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=1,
                total_installments=6,
                amount=Money(Decimal("5000.00"), Currency.ARS),
                billing_period="20251",
            )

    def test_raises_error_for_billing_period_too_long(self):
        """
        GIVEN: billing_period with more than 6 digits
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="billing_period must be in YYYYMM format"):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=1,
                total_installments=6,
                amount=Money(Decimal("5000.00"), Currency.ARS),
                billing_period="2025011",
            )

    def test_raises_error_for_billing_period_with_letters(self):
        """
        GIVEN: billing_period with non-numeric characters
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="billing_period must be in YYYYMM format"):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=1,
                total_installments=6,
                amount=Money(Decimal("5000.00"), Currency.ARS),
                billing_period="2025AB",
            )

    def test_raises_error_for_invalid_month_zero(self):
        """
        GIVEN: billing_period with month = 00
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="billing_period month must be between 01-12"
        ):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=1,
                total_installments=6,
                amount=Money(Decimal("5000.00"), Currency.ARS),
                billing_period="202500",
            )

    def test_raises_error_for_invalid_month_thirteen(self):
        """
        GIVEN: billing_period with month = 13
        WHEN: Creating an Installment
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="billing_period month must be between 01-12"
        ):
            Installment(
                id=None,
                purchase_id=100,
                installment_number=1,
                total_installments=6,
                amount=Money(Decimal("5000.00"), Currency.ARS),
                billing_period="202513",
            )

    @pytest.mark.parametrize(
        "valid_period",
        [
            "202501",  # January
            "202506",  # June
            "202512",  # December
            "203001",  # Future year
            "199912",  # Past year
        ],
    )
    def test_accepts_valid_billing_periods(self, valid_period):
        """
        GIVEN: Valid billing_period in YYYYMM format
        WHEN: Creating an Installment
        THEN: Should accept the period
        """
        # Arrange & Act
        installment = Installment(
            id=None,
            purchase_id=100,
            installment_number=1,
            total_installments=6,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period=valid_period,
        )

        # Assert
        assert installment.billing_period == valid_period

    # ===== EQUALITY & IMMUTABILITY =====

    def test_installments_with_same_id_are_equal(self):
        """
        GIVEN: Two installments with same ID but different attributes
        WHEN: Comparing them
        THEN: Should be equal
        """
        # Arrange
        installment1 = Installment(
            id=1,
            purchase_id=100,
            installment_number=1,
            total_installments=6,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202501",
        )
        installment2 = Installment(
            id=1,
            purchase_id=999,
            installment_number=6,
            total_installments=12,
            amount=Money(Decimal("1000.00"), Currency.USD),
            billing_period="202512",
        )

        # Act & Assert
        assert installment1 == installment2

    def test_installments_with_different_ids_are_not_equal(self):
        """
        GIVEN: Two installments with different IDs
        WHEN: Comparing them
        THEN: Should not be equal
        """
        # Arrange
        installment1 = Installment(
            id=1,
            purchase_id=100,
            installment_number=1,
            total_installments=6,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202501",
        )
        installment2 = Installment(
            id=2,
            purchase_id=100,
            installment_number=1,
            total_installments=6,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202501",
        )

        # Act & Assert
        assert installment1 != installment2

    def test_new_installments_without_id_are_not_equal(self):
        """
        GIVEN: Two new installments without ID (both None)
        WHEN: Comparing them
        THEN: Should not be equal (reference equality)
        """
        # Arrange
        installment1 = Installment(
            id=None,
            purchase_id=100,
            installment_number=1,
            total_installments=6,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202501",
        )
        installment2 = Installment(
            id=None,
            purchase_id=100,
            installment_number=1,
            total_installments=6,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202501",
        )

        # Act & Assert
        assert installment1 != installment2

    def test_installment_is_not_equal_to_other_types(self):
        """
        GIVEN: An installment and a different type object
        WHEN: Comparing them
        THEN: Should not be equal
        """
        # Arrange
        installment = Installment(
            id=1,
            purchase_id=100,
            installment_number=1,
            total_installments=6,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202501",
        )

        # Act & Assert
        assert installment != "not an installment"
        assert installment != 1
        assert installment != None

    def test_installment_is_immutable(self):
        """
        GIVEN: An Installment instance
        WHEN: Trying to modify an attribute
        THEN: Should raise FrozenInstanceError
        """
        # Arrange
        installment = Installment(
            id=1,
            purchase_id=100,
            installment_number=1,
            total_installments=6,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202501",
        )

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            installment.amount = Money(Decimal("6000.00"), Currency.ARS)

    def test_installment_can_be_used_in_set(self):
        """
        GIVEN: Multiple Installment instances
        WHEN: Adding them to a set
        THEN: Should work correctly (hashable)
        """
        # Arrange
        installment1 = Installment(
            id=1,
            purchase_id=100,
            installment_number=1,
            total_installments=6,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202501",
        )
        installment2 = Installment(
            id=2,
            purchase_id=100,
            installment_number=2,
            total_installments=6,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202502",
        )
        installment3 = Installment(
            id=1,
            purchase_id=999,
            installment_number=99,
            total_installments=99,
            amount=Money(Decimal("1.00"), Currency.USD),
            billing_period="203012",
        )

        # Act
        installment_set = {installment1, installment2, installment3}

        # Assert
        assert len(installment_set) == 2  # installment1 and installment3 have same ID

    # ===== EDGE CASES =====

    def test_installment_with_minimal_amount(self):
        """
        GIVEN: Installment with minimal positive amount
        WHEN: Creating an Installment
        THEN: Should accept small amounts
        """
        # Arrange & Act
        installment = Installment(
            id=1,
            purchase_id=100,
            installment_number=1,
            total_installments=1,
            amount=Money(Decimal("0.01"), Currency.ARS),
            billing_period="202501",
        )

        # Assert
        assert installment.amount.amount == Decimal("0.01")

    def test_installment_with_very_large_amount(self):
        """
        GIVEN: Installment with very large amount
        WHEN: Creating an Installment
        THEN: Should handle large numbers correctly
        """
        # Arrange & Act
        installment = Installment(
            id=1,
            purchase_id=100,
            installment_number=1,
            total_installments=1,
            amount=Money(Decimal("999999999.99"), Currency.ARS),
            billing_period="202501",
        )

        # Assert
        assert installment.amount.amount == Decimal("999999999.99")

    def test_installment_with_many_total_installments(self):
        """
        GIVEN: Installment from purchase with many installments
        WHEN: Creating an Installment
        THEN: Should handle large totals
        """
        # Arrange & Act
        installment = Installment(
            id=1,
            purchase_id=100,
            installment_number=60,
            total_installments=60,
            amount=Money(Decimal("1666.67"), Currency.ARS),
            billing_period="203001",
        )

        # Assert
        assert installment.installment_number == 60
        assert installment.total_installments == 60
