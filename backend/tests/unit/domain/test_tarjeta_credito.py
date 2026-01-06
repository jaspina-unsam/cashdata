import pytest
from decimal import Decimal
from datetime import date
from dataclasses import FrozenInstanceError
from app.domain.entities.credit_card import CreditCard
from app.domain.value_objects.money import Money, Currency


class TestTarjetaCreditoEntity:
    """Unit tests for TarjetaCredito domain entity"""

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

    def test_create_tarjeta_with_all_fields(self, valid_card_data):
        """GIVEN: Valid card data, WHEN: Create entity, THEN: Success"""
        tarjeta = CreditCard(**valid_card_data)

        assert tarjeta.id == 1
        assert tarjeta.user_id == 1
        assert tarjeta.name == "Visa HSBC"
        assert tarjeta.bank == "HSBC"
        assert tarjeta.last_four_digits == "1234"
        assert tarjeta.billing_close_day == 10
        assert tarjeta.payment_due_day == 20
        assert tarjeta.credit_limit == Money(Decimal("100000"), Currency.ARS)

    def test_create_card_without_limit(self, valid_card_data):
        """GIVEN: Card without limit, WHEN: Create, THEN: Limit is None"""
        # Arrange
        del valid_card_data["credit_limit"]

        # Act
        tarjeta = CreditCard(**valid_card_data)

        # Assert
        assert tarjeta.credit_limit is None

    def test_create_card_without_id(self, valid_card_data):
        """GIVEN: Card data without ID (new entity), WHEN: Create, THEN: ID should be None"""
        # Arrange
        valid_card_data["id"] = None

        # Act
        tarjeta = CreditCard(**valid_card_data)

        # Assert
        assert tarjeta.id is None

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
        tarjeta = CreditCard(**valid_card_data)
        fecha_compra = date(2025, 1, 5)

        # Act
        periodo = tarjeta.calculate_billing_period(fecha_compra)

        # Assert
        assert periodo == "202501"

    def test_calculate_billing_period_after_closing_date(self, valid_card_data):
        """
        GIVEN: Card with closure day 10
        WHEN: Purchase on January 15 (after closure)
        THEN: Period should be "202502" (next month)
        """
        # Arrange
        tarjeta = CreditCard(**valid_card_data)
        fecha_compra = date(2025, 1, 15)

        # Act
        periodo = tarjeta.calculate_billing_period(fecha_compra)

        # Assert
        assert periodo == "202502"

    def test_calculate_billing_period_on_closing_date(self, valid_card_data):
        """
        GIVEN: Card with closure day 10
        WHEN: Purchase on January 10 (exact closure day)
        THEN: Period should be "202501" (same month, inclusive)
        """
        # Arrange
        tarjeta = CreditCard(**valid_card_data)
        fecha_compra = date(2025, 1, 10)

        # Act
        periodo = tarjeta.calculate_billing_period(fecha_compra)

        # Assert
        assert periodo == "202501"

    def test_calculate_billing_period_handles_year_transition(self, valid_card_data):
        """
        GIVEN: Card with closure day 10
        WHEN: Purchase on December 15, 2024
        THEN: Period should be "202501" (next year)
        """
        # Arrange
        tarjeta = CreditCard(**valid_card_data)
        fecha_compra = date(2024, 12, 15)

        # Act
        periodo = tarjeta.calculate_billing_period(fecha_compra)

        # Assert
        assert periodo == "202501"

    # ===== DUE DATE CALCULATION =====

    def test_normal_calculate_due_date(self, valid_card_data):
        """
        GIVEN: Card with due day 20, closure day 10
        WHEN: Calculate due date for period "202501"
        THEN: Should return 2025-01-20 (same month)
        """
        # Arrange
        tarjeta = CreditCard(**valid_card_data)

        # Act
        fecha_vencimiento = tarjeta.calculate_due_date("202501")

        # Assert
        assert fecha_vencimiento == date(2025, 1, 20)

    def test_calculate_due_date_next_month(self):
        """
        GIVEN: Card with due day 5, closure day 25 (due < closure)
        WHEN: Calculate due date for period "202501"
        THEN: Should return 2025-02-05 (next month)
        """
        # Arrange
        tarjeta = CreditCard(
            id=1,
            user_id=1,
            name="Visa HSBC",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=25,
            payment_due_day=5,
            credit_limit=None,
        )

        # Act
        fecha_vencimiento = tarjeta.calculate_due_date("202501")

        # Assert
        assert fecha_vencimiento == date(2025, 2, 5)

    def test_calculate_due_date_handles_invalid_day_in_month(self):
        """
        GIVEN: Card with due day 31
        WHEN: Calculate due date for period "202502" (February)
        THEN: Should return last day of February (28 or 29)
        """
        # Arrange
        tarjeta = CreditCard(
            id=1,
            user_id=1,
            name="Visa HSBC",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=25,
            payment_due_day=31,
            credit_limit=None,
        )

        # Act
        fecha_vencimiento = tarjeta.calculate_due_date("202502")

        # Assert
        assert fecha_vencimiento == date(2025, 2, 28)  # 2025 is not a leap year

    def test_calculate_due_date_leap_year(self):
        """
        GIVEN: Card with due day 31
        WHEN: Calculate due date for period "202402" (February 2024, leap year)
        THEN: Should return 2024-02-29
        """
        # Arrange
        tarjeta = CreditCard(
            id=1,
            user_id=1,
            name="Visa HSBC",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=25,
            payment_due_day=31,
            credit_limit=None,
        )

        # Act
        fecha_vencimiento = tarjeta.calculate_due_date("202402")

        # Assert
        assert fecha_vencimiento == date(2024, 2, 29)  # 2024 is a leap year

    # ===== EQUALITY =====

    def test_cards_equal_by_id(self, valid_card_data):
        """
        GIVEN: Two cards with same ID
        WHEN: Comparing them
        THEN: They should be equal
        """
        # Arrange
        tarjeta1 = CreditCard(**valid_card_data)
        valid_card_data["name"] = "Otro Nombre"
        tarjeta2 = CreditCard(**valid_card_data)

        # Act & Assert
        assert tarjeta1 == tarjeta2

    def test_cards_not_equal_different_id(self, valid_card_data):
        """
        GIVEN: Two cards with different IDs
        WHEN: Comparing them
        THEN: They should not be equal
        """
        # Arrange
        tarjeta1 = CreditCard(**valid_card_data)
        valid_card_data["id"] = 2
        tarjeta2 = CreditCard(**valid_card_data)

        # Act & Assert
        assert tarjeta1 != tarjeta2

    def test_new_cards_not_equal(self, valid_card_data):
        """
        GIVEN: Two new cards (id=None) with same data
        WHEN: Comparing them
        THEN: They should not be equal (different instances)
        """
        # Arrange
        valid_card_data["id"] = None
        tarjeta1 = CreditCard(**valid_card_data)
        tarjeta2 = CreditCard(**valid_card_data)

        # Act & Assert
        assert tarjeta1 != tarjeta2

    # ===== IMMUTABILITY =====

    def test_card_is_immutable(self, valid_card_data):
        """
        GIVEN: A TarjetaCredito instance
        WHEN: Trying to modify a field
        THEN: Should raise FrozenInstanceError
        """
        # Arrange
        tarjeta = CreditCard(**valid_card_data)

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            tarjeta.name = "Nuevo Nombre"
