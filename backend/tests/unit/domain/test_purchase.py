import pytest
from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

from cashdata.domain.entities.purchase import Purchase
from cashdata.domain.value_objects.money import Money, Currency


class TestPurchaseEntity:
    """Unit tests for Purchase domain entity"""

    # ===== HAPPY PATH =====

    def test_create_purchase_with_single_payment(self):
        """
        GIVEN: Valid purchase data with single payment (installments_count=1)
        WHEN: Creating a Purchase
        THEN: Entity is created successfully
        """
        # Arrange & Act
        purchase = Purchase(
            id=1,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Laptop Dell",
            total_amount=Money(Decimal("150000.00"), Currency.ARS),
            installments_count=1,
        )

        # Assert
        assert purchase.id == 1
        assert purchase.user_id == 10
        assert purchase.credit_card_id == 5
        assert purchase.category_id == 3
        assert purchase.purchase_date == date(2025, 1, 15)
        assert purchase.description == "Laptop Dell"
        assert purchase.total_amount.amount == Decimal("150000.00")
        assert purchase.total_amount.currency == Currency.ARS
        assert purchase.installments_count == 1

    def test_create_purchase_with_multiple_installments(self):
        """
        GIVEN: Valid purchase data with multiple installments
        WHEN: Creating a Purchase
        THEN: Entity is created successfully
        """
        # Arrange & Act
        purchase = Purchase(
            id=None,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Smart TV 55 pulgadas",
            total_amount=Money(Decimal("85000.00"), Currency.ARS),
            installments_count=12,
        )

        # Assert
        assert purchase.id is None
        assert purchase.installments_count == 12
        assert purchase.description == "Smart TV 55 pulgadas"

    def test_create_purchase_without_id(self):
        """
        GIVEN: Purchase data without ID (new entity)
        WHEN: Creating a Purchase
        THEN: ID should be None
        """
        # Arrange & Act
        purchase = Purchase(
            id=None,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Supermercado",
            total_amount=Money(Decimal("25000.00"), Currency.ARS),
            installments_count=1,
        )

        # Assert
        assert purchase.id is None

    def test_strips_whitespace_from_description(self):
        """
        GIVEN: Purchase description with leading/trailing spaces
        WHEN: Creating a Purchase
        THEN: Description should be trimmed
        """
        # Arrange & Act
        purchase = Purchase(
            id=1,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="  Cena en restaurante  ",
            total_amount=Money(Decimal("8500.00"), Currency.ARS),
            installments_count=1,
        )

        # Assert
        assert purchase.description == "Cena en restaurante"

    def test_purchase_with_usd_currency(self):
        """
        GIVEN: Purchase with USD currency
        WHEN: Creating a Purchase
        THEN: Currency is preserved
        """
        # Arrange & Act
        purchase = Purchase(
            id=1,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Amazon purchase",
            total_amount=Money(Decimal("250.00"), Currency.USD),
            installments_count=3,
        )

        # Assert
        assert purchase.total_amount.currency == Currency.USD

    # ===== VALIDATION ERRORS =====

    def test_raises_error_for_zero_installments(self):
        """
        GIVEN: installments_count = 0
        WHEN: Creating a Purchase
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="installments_count must be >= 1"):
            Purchase(
                id=None,
                user_id=10,
                credit_card_id=5,
                category_id=3,
                purchase_date=date(2025, 1, 15),
                description="Invalid purchase",
                total_amount=Money(Decimal("1000.00"), Currency.ARS),
                installments_count=0,
            )

    def test_raises_error_for_negative_installments(self):
        """
        GIVEN: installments_count < 0
        WHEN: Creating a Purchase
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="installments_count must be >= 1"):
            Purchase(
                id=None,
                user_id=10,
                credit_card_id=5,
                category_id=3,
                purchase_date=date(2025, 1, 15),
                description="Invalid purchase",
                total_amount=Money(Decimal("1000.00"), Currency.ARS),
                installments_count=-1,
            )

    def test_raises_error_for_zero_amount(self):
        """
        GIVEN: total_amount = 0
        WHEN: Creating a Purchase
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="total_amount must be positive"):
            Purchase(
                id=None,
                user_id=10,
                credit_card_id=5,
                category_id=3,
                purchase_date=date(2025, 1, 15),
                description="Invalid purchase",
                total_amount=Money(Decimal("0.00"), Currency.ARS),
                installments_count=1,
            )

    def test_raises_error_for_negative_amount(self):
        """
        GIVEN: total_amount < 0
        WHEN: Creating a Purchase
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="total_amount must be positive"):
            Purchase(
                id=None,
                user_id=10,
                credit_card_id=5,
                category_id=3,
                purchase_date=date(2025, 1, 15),
                description="Invalid purchase",
                total_amount=Money(Decimal("-100.00"), Currency.ARS),
                installments_count=1,
            )

    def test_raises_error_for_empty_description(self):
        """
        GIVEN: Empty string as description
        WHEN: Creating a Purchase
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="description cannot be empty"):
            Purchase(
                id=None,
                user_id=10,
                credit_card_id=5,
                category_id=3,
                purchase_date=date(2025, 1, 15),
                description="",
                total_amount=Money(Decimal("1000.00"), Currency.ARS),
                installments_count=1,
            )

    def test_raises_error_for_whitespace_only_description(self):
        """
        GIVEN: Description with only spaces
        WHEN: Creating a Purchase
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="description cannot be empty"):
            Purchase(
                id=None,
                user_id=10,
                credit_card_id=5,
                category_id=3,
                purchase_date=date(2025, 1, 15),
                description="   ",
                total_amount=Money(Decimal("1000.00"), Currency.ARS),
                installments_count=1,
            )

    # ===== EQUALITY & IMMUTABILITY =====

    def test_purchases_with_same_id_are_equal(self):
        """
        GIVEN: Two purchases with same ID but different attributes
        WHEN: Comparing them
        THEN: Should be equal
        """
        # Arrange
        purchase1 = Purchase(
            id=1,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Purchase A",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )
        purchase2 = Purchase(
            id=1,
            user_id=99,
            credit_card_id=99,
            category_id=99,
            purchase_date=date(2025, 12, 31),
            description="Purchase B",
            total_amount=Money(Decimal("5000.00"), Currency.ARS),
            installments_count=6,
        )

        # Act & Assert
        assert purchase1 == purchase2

    def test_purchases_with_different_ids_are_not_equal(self):
        """
        GIVEN: Two purchases with different IDs
        WHEN: Comparing them
        THEN: Should not be equal
        """
        # Arrange
        purchase1 = Purchase(
            id=1,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Purchase A",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )
        purchase2 = Purchase(
            id=2,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Purchase A",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )

        # Act & Assert
        assert purchase1 != purchase2

    def test_new_purchases_without_id_are_not_equal(self):
        """
        GIVEN: Two new purchases without ID (both None)
        WHEN: Comparing them
        THEN: Should not be equal (reference equality)
        """
        # Arrange
        purchase1 = Purchase(
            id=None,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Purchase A",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )
        purchase2 = Purchase(
            id=None,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Purchase A",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )

        # Act & Assert
        assert purchase1 != purchase2

    def test_purchase_is_not_equal_to_other_types(self):
        """
        GIVEN: A purchase and a different type object
        WHEN: Comparing them
        THEN: Should not be equal
        """
        # Arrange
        purchase = Purchase(
            id=1,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Purchase A",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )

        # Act & Assert
        assert purchase != "not a purchase"
        assert purchase != 1
        assert purchase != None

    def test_purchase_is_immutable(self):
        """
        GIVEN: A Purchase instance
        WHEN: Trying to modify an attribute
        THEN: Should raise FrozenInstanceError
        """
        # Arrange
        purchase = Purchase(
            id=1,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Purchase A",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            purchase.description = "Modified"

    def test_purchase_can_be_used_in_set(self):
        """
        GIVEN: Multiple Purchase instances
        WHEN: Adding them to a set
        THEN: Should work correctly (hashable)
        """
        # Arrange
        purchase1 = Purchase(
            id=1,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Purchase A",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )
        purchase2 = Purchase(
            id=2,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Purchase B",
            total_amount=Money(Decimal("2000.00"), Currency.ARS),
            installments_count=1,
        )
        purchase3 = Purchase(
            id=1,
            user_id=99,
            credit_card_id=99,
            category_id=99,
            purchase_date=date(2025, 12, 31),
            description="Purchase C",
            total_amount=Money(Decimal("3000.00"), Currency.ARS),
            installments_count=1,
        )

        # Act
        purchase_set = {purchase1, purchase2, purchase3}

        # Assert
        assert len(purchase_set) == 2  # purchase1 and purchase3 have same ID

    # ===== EDGE CASES =====

    def test_purchase_with_very_large_amount(self):
        """
        GIVEN: Purchase with very large amount
        WHEN: Creating a Purchase
        THEN: Should handle large numbers correctly
        """
        # Arrange & Act
        purchase = Purchase(
            id=1,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Expensive item",
            total_amount=Money(Decimal("999999999.99"), Currency.ARS),
            installments_count=1,
        )

        # Assert
        assert purchase.total_amount.amount == Decimal("999999999.99")

    def test_purchase_with_many_installments(self):
        """
        GIVEN: Purchase with many installments
        WHEN: Creating a Purchase
        THEN: Should handle large installment counts
        """
        # Arrange & Act
        purchase = Purchase(
            id=1,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Long term financing",
            total_amount=Money(Decimal("100000.00"), Currency.ARS),
            installments_count=60,
        )

        # Assert
        assert purchase.installments_count == 60

    def test_purchase_with_minimal_amount(self):
        """
        GIVEN: Purchase with minimal positive amount
        WHEN: Creating a Purchase
        THEN: Should accept small amounts
        """
        # Arrange & Act
        purchase = Purchase(
            id=1,
            user_id=10,
            credit_card_id=5,
            category_id=3,
            purchase_date=date(2025, 1, 15),
            description="Small purchase",
            total_amount=Money(Decimal("0.01"), Currency.ARS),
            installments_count=1,
        )

        # Assert
        assert purchase.total_amount.amount == Decimal("0.01")
