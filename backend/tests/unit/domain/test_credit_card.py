import pytest
from decimal import Decimal
from datetime import date
from dataclasses import FrozenInstanceError
from app.domain.entities.credit_card import CreditCard
from app.domain.value_objects.money import Money, Currency


class TestCreditCardEntity:
    """Unit tests for CreditCard domain entity"""

    @pytest.fixture
    def valid_card_data(self):
        """Default valid card data"""
        return {
            "id": 1,
            "user_id": 1,
            "name": "Visa HSBC",
            "bank": "HSBC",
            "last_four_digits": "1234",
            "billing_close_day": 10,
            "payment_due_day": 20,
            "credit_limit": Money(Decimal("100000"), Currency.ARS),
        }

    # ===== HAPPY PATH =====

    def test_create_card_with_all_fields(self, valid_card_data):
        """GIVEN: Valid card data, WHEN: Create entity, THEN: Success"""
        card = CreditCard(**valid_card_data)

        assert card.id == 1
        assert card.user_id == 1
        assert card.name == "Visa HSBC"
        assert card.bank == "HSBC"
        assert card.last_four_digits == "1234"
        assert card.billing_close_day == 10
        assert card.payment_due_day == 20
        assert card.credit_limit == Money(Decimal("100000"), Currency.ARS)

    def test_create_card_without_limit(self, valid_card_data):
        """GIVEN: Card without limit, WHEN: Create, THEN: Limit is None"""
        # Arrange
        del valid_card_data["credit_limit"]

        # Act
        card = CreditCard(**valid_card_data)

        # Assert
        assert card.credit_limit is None

    def test_create_card_without_id(self, valid_card_data):
        """GIVEN: Card data without ID (new entity), WHEN: Create, THEN: ID should be None"""
        # Arrange
        valid_card_data["id"] = None

        # Act
        card = CreditCard(**valid_card_data)

        # Assert
        assert card.id is None

    # ===== VALIDATIONS =====
    @pytest.mark.parametrize("invalid_day", [0, 32, -1, 100])
    def test_invalid_billing_close_day_raises_error(self, valid_card_data, invalid_day):
        """GIVEN: Invalid closure day, WHEN: Create, THEN: ValueError"""
        # Arrange
        valid_card_data["billing_close_day"] = invalid_day

        # Act & Assert
        with pytest.raises(ValueError, match="billing_close_day must be between 1-31"):
            CreditCard(**valid_card_data)

    @pytest.mark.parametrize("invalid_day", [0, 32, -1, 100])
    def test_invalid_payment_due_day_raises_error(
        self, valid_card_data, invalid_day
    ):
        """GIVEN: Invalid due day, WHEN: Create, THEN: ValueError"""
        # Arrange
        valid_card_data["payment_due_day"] = invalid_day

        # Act & Assert
        with pytest.raises(ValueError, match="payment_due_day must be between 1-31"):
            CreditCard(**valid_card_data)

    @pytest.mark.parametrize("invalid_digits", ["123", "12345", "abcd", "12a4"])
    def test_invalid_last_four_digits_raises_error(
        self, valid_card_data, invalid_digits
    ):
        """GIVEN: Invalid last 4 digits, WHEN: Create, THEN: ValueError"""
        # Arrange
        valid_card_data["last_four_digits"] = invalid_digits

        # Act & Assert
        with pytest.raises(ValueError):
            CreditCard(**valid_card_data)

    def test_empty_name_raises_error(self, valid_card_data):
        """GIVEN: Empty nombre, WHEN: Create, THEN: ValueError"""
        # Arrange
        valid_card_data["name"] = ""

        # Act & Assert
        with pytest.raises(ValueError, match="name cannot be empty"):
            CreditCard(**valid_card_data)

    def test_whitespace_name_raises_error(self, valid_card_data):
        """GIVEN: Whitespace-only nombre, WHEN: Create, THEN: ValueError"""
        # Arrange
        valid_card_data["name"] = "   "

        # Act & Assert
        with pytest.raises(ValueError, match="name cannot be empty"):
            CreditCard(**valid_card_data)

    # ===== BILLING PERIOD CALCULATION =====

    def test_calculate_billing_period_before_closing_date(self, valid_card_data):
        """
        GIVEN: Card with closure day 10
        WHEN: Purchase on January 5 (before closure)
        THEN: Period should be "202501" (same month)
        """
        # Arrange
        card = CreditCard(**valid_card_data)
        fecha_compra = date(2025, 1, 5)

        # Act
        periodo = card.calculate_billing_period(fecha_compra)

        # Assert
        assert periodo == "202501"

    def test_calculate_billing_period_after_closing_date(self, valid_card_data):
        """
        GIVEN: Card with closure day 10
        WHEN: Purchase on January 15 (after closure)
        THEN: Period should be "202502" (next month)
        """
        # Arrange
        card = CreditCard(**valid_card_data)
        fecha_compra = date(2025, 1, 15)

        # Act
        periodo = card.calculate_billing_period(fecha_compra)

        # Assert
        assert periodo == "202502"

    def test_calculate_billing_period_on_closing_date(self, valid_card_data):
        """
        GIVEN: Card with closure day 10
        WHEN: Purchase on January 10 (exact closure day)
        THEN: Period should be "202501" (same month, inclusive)
        """
        # Arrange
        card = CreditCard(**valid_card_data)
        fecha_compra = date(2025, 1, 10)

        # Act
        periodo = card.calculate_billing_period(fecha_compra)

        # Assert
        assert periodo == "202501"

    def test_calculate_billing_period_handles_year_transition(self, valid_card_data):
        """
        GIVEN: Card with closure day 10
        WHEN: Purchase on December 15, 2024
        THEN: Period should be "202501" (next year)
        """
        # Arrange
        card = CreditCard(**valid_card_data)
        fecha_compra = date(2024, 12, 15)

        # Act
        periodo = card.calculate_billing_period(fecha_compra)

        # Assert
        assert periodo == "202501"
    # ===== EQUALITY =====

    def test_cards_equal_by_id(self, valid_card_data):
        """
        GIVEN: Two cards with same ID
        WHEN: Comparing them
        THEN: They should be equal
        """
        # Arrange
        card1 = CreditCard(**valid_card_data)
        valid_card_data["name"] = "Otro Nombre"
        card2 = CreditCard(**valid_card_data)

        # Act & Assert
        assert card1 == card2

    def test_cards_not_equal_different_id(self, valid_card_data):
        """
        GIVEN: Two cards with different IDs
        WHEN: Comparing them
        THEN: They should not be equal
        """
        # Arrange
        card1 = CreditCard(**valid_card_data)
        valid_card_data["id"] = 2
        card2 = CreditCard(**valid_card_data)

        # Act & Assert
        assert card1 != card2

    def test_new_cards_not_equal(self, valid_card_data):
        """
        GIVEN: Two new cards (id=None) with same data
        WHEN: Comparing them
        THEN: They should not be equal (different instances)
        """
        # Arrange
        valid_card_data["id"] = None
        card1 = CreditCard(**valid_card_data)
        card2 = CreditCard(**valid_card_data)

        # Act & Assert
        assert card1 != card2

    # ===== IMMUTABILITY =====

    def test_card_is_immutable(self, valid_card_data):
        """
        GIVEN: A CreditCard instance
        WHEN: Trying to modify a field
        THEN: Should raise FrozenInstanceError
        """
        # Arrange
        card = CreditCard(**valid_card_data)

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            card.name = "Nuevo Nombre"
