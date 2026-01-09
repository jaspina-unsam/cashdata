import pytest
from datetime import date
from decimal import Decimal

from app.domain.services.installment_generator import InstallmentGenerator
from app.domain.entities.credit_card import CreditCard
from app.domain.value_objects.money import Money, Currency
from app.domain.exceptions.domain_exceptions import InvalidCalculation


class TestInstallmentGenerator:
    """Unit tests for InstallmentGenerator domain service"""

    # ===== HAPPY PATH - SINGLE PAYMENT =====

    def test_generate_single_installment(self):
        """
        GIVEN: Purchase with single payment (1 installment)
        WHEN: Generating installments
        THEN: Should create one installment with full amount
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        total_amount = Money(Decimal("10000.00"), Currency.ARS)
        purchase_date = date(2025, 1, 15)

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=total_amount,
            installments_count=1,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Assert
        assert len(installments) == 1
        assert installments[0].purchase_id == 100
        assert installments[0].installment_number == 1
        assert installments[0].total_installments == 1
        assert installments[0].amount.amount == Decimal("10000.00")
        assert installments[0].amount.currency == Currency.ARS
        assert installments[0].billing_period == "202502"  # After close 10 → Feb statement
        assert installments[0].id is None

    # ===== HAPPY PATH - EXACT DIVISION =====

    def test_generate_installments_with_exact_division(self):
        """
        GIVEN: Purchase with amount that divides evenly
        WHEN: Generating installments
        THEN: All installments should have equal amounts
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        total_amount = Money(Decimal("12000.00"), Currency.ARS)
        purchase_date = date(2025, 1, 5)  # Before close day

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=total_amount,
            installments_count=6,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Assert
        assert len(installments) == 6
        for i, installment in enumerate(installments, 1):
            assert installment.installment_number == i
            assert installment.total_installments == 6
            assert installment.amount.amount == Decimal("2000.00")

    # ===== HAPPY PATH - DIVISION WITH REMAINDER =====

    def test_generate_installments_with_remainder(self):
        """
        GIVEN: Purchase with amount that doesn't divide evenly
        WHEN: Generating installments
        THEN: First installment should absorb remainder
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        total_amount = Money(Decimal("10000.00"), Currency.ARS)
        purchase_date = date(2025, 1, 5)

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=total_amount,
            installments_count=3,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Assert
        assert len(installments) == 3
        # 10000 / 3 = 3333.33 per installment (rounded to cents)
        # First installment: 3333.33 + 0.01 remainder = 3333.34
        assert installments[0].amount.amount == Decimal("3333.34")
        assert installments[1].amount.amount == Decimal("3333.33")
        assert installments[2].amount.amount == Decimal("3333.33")

        # Verify total sum equals original amount
        total_sum = sum(inst.amount.amount for inst in installments)
        assert total_sum == Decimal("10000.00")

    def test_sum_of_installments_equals_total_amount(self):
        """
        GIVEN: Any purchase with installments
        WHEN: Generating installments
        THEN: Sum of all installments must equal total amount (no rounding errors)
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        test_cases = [
            (Decimal("10000.00"), 3),  # 10000 / 3 = 3333.33...
            (Decimal("99999.99"), 7),  # 99999.99 / 7 = 14285.71...
            (Decimal("1000.01"), 12),  # 1000.01 / 12 = 83.33...
            (Decimal("50000.00"), 24),  # 50000 / 24 = 2083.33...
        ]

        for amount, count in test_cases:
            # Act
            installments = InstallmentGenerator.generate_installments(
                purchase_id=100,
                total_amount=Money(amount, Currency.ARS),
                installments_count=count,
                purchase_date=date(2025, 1, 5),
                credit_card=credit_card,
            )

            # Assert
            total_sum = sum(inst.amount.amount for inst in installments)
            assert total_sum == amount, f"Sum mismatch for {amount}/{count}"

    # ===== BILLING PERIOD CALCULATION =====

    def test_billing_periods_are_sequential(self):
        """
        GIVEN: Purchase with multiple installments
        WHEN: Generating installments
        THEN: Billing periods should be sequential months
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        total_amount = Money(Decimal("6000.00"), Currency.ARS)
        purchase_date = date(2025, 1, 5)

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=total_amount,
            installments_count=6,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Assert - Sequential periods starting from statement month
        # Purchase Jan 5 (before close 10) → Jan statement → period 202501
        expected_periods = ["202501", "202502", "202503", "202504", "202505", "202506"]
        actual_periods = [inst.billing_period for inst in installments]
        assert actual_periods == expected_periods

    def test_billing_periods_span_year_transition(self):
        """
        GIVEN: Purchase near end of year
        WHEN: Generating installments across year boundary
        THEN: Periods should correctly transition to next year
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        total_amount = Money(Decimal("6000.00"), Currency.ARS)
        purchase_date = date(2025, 10, 5)

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=total_amount,
            installments_count=6,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Assert - Verify year transition
        # Purchase Oct 5 (before close 10) → Oct statement → period 202510
        expected_periods = ["202510", "202511", "202512", "202601", "202602", "202603"]
        actual_periods = [inst.billing_period for inst in installments]
        assert actual_periods == expected_periods

    def test_purchase_on_close_day_current_period(self):
        """
        GIVEN: Purchase on the close day
        WHEN: Generating installments
        THEN: First installment should be in current period
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        total_amount = Money(Decimal("3000.00"), Currency.ARS)
        purchase_date = date(2025, 1, 10)  # Exactly on close day

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=total_amount,
            installments_count=3,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Purchase on Jan 10 (close day) → Jan 10 statement → period 202501
        assert installments[0].billing_period == "202501"  # Jan statement
        assert installments[1].billing_period == "202502"  # Feb statement
        assert installments[2].billing_period == "202503"  # Mar statement

    def test_purchase_after_close_day_next_period(self):
        """
        GIVEN: Purchase after the close day
        WHEN: Generating installments
        THEN: First installment should be in next period
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        total_amount = Money(Decimal("3000.00"), Currency.ARS)
        purchase_date = date(2025, 1, 15)  # After close day

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=total_amount,
            installments_count=3,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Assert - Purchase after close day goes to next statement
        # Purchase Jan 15 (after close 10) → Feb 10 statement → period 202502
        assert installments[0].billing_period == "202502"  # Feb statement
        assert installments[1].billing_period == "202503"  # Mar statement
        assert installments[2].billing_period == "202504"  # Apr statement

    # ===== VALIDATION ERRORS =====

    def test_raises_error_for_zero_installments(self):
        """
        GIVEN: installments_count = 0
        WHEN: Generating installments
        THEN: Should raise InvalidCalculation
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )

        # Act & Assert
        with pytest.raises(InvalidCalculation, match="installments_count must be >= 1"):
            InstallmentGenerator.generate_installments(
                purchase_id=100,
                total_amount=Money(Decimal("1000.00"), Currency.ARS),
                installments_count=0,
                purchase_date=date(2025, 1, 15),
                credit_card=credit_card,
            )

    def test_raises_error_for_negative_installments(self):
        """
        GIVEN: installments_count < 0
        WHEN: Generating installments
        THEN: Should raise InvalidCalculation
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )

        # Act & Assert
        with pytest.raises(InvalidCalculation, match="installments_count must be >= 1"):
            InstallmentGenerator.generate_installments(
                purchase_id=100,
                total_amount=Money(Decimal("1000.00"), Currency.ARS),
                installments_count=-5,
                purchase_date=date(2025, 1, 15),
                credit_card=credit_card,
            )

    def test_raises_error_for_zero_amount(self):
        """
        GIVEN: total_amount = 0
        WHEN: Generating installments
        THEN: Should raise InvalidCalculation
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )

        # Act & Assert
        with pytest.raises(InvalidCalculation, match="total_amount cannot be zero"):
            InstallmentGenerator.generate_installments(
                purchase_id=100,
                total_amount=Money(Decimal("0.00"), Currency.ARS),
                installments_count=3,
                purchase_date=date(2025, 1, 15),
                credit_card=credit_card,
            )

    def test_allows_negative_amount_for_credits(self):
        """
        GIVEN: total_amount < 0 (credit/bonification)
        WHEN: Generating installments
        THEN: Should succeed and generate negative installments
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=Money(Decimal("-1000.00"), Currency.ARS),
            installments_count=1,
            purchase_date=date(2025, 1, 15),
            credit_card=credit_card,
        )

        # Assert
        assert len(installments) == 1
        assert installments[0].amount.amount == Decimal("-1000.00")

    # ===== EDGE CASES =====

    def test_many_installments(self):
        """
        GIVEN: Purchase with many installments (24)
        WHEN: Generating installments
        THEN: Should handle large installment counts correctly
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        total_amount = Money(Decimal("24000.00"), Currency.ARS)
        purchase_date = date(2025, 1, 5)

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=total_amount,
            installments_count=24,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Assert
        assert len(installments) == 24
        # All equal amounts (exact division)
        for inst in installments:
            assert inst.amount.amount == Decimal("1000.00")

        # First: Purchase Jan 5 (before close 10) → Jan statement → period 202501
        # Last (24th): 23 months later → Dec 2026 statement → period 202612
        assert installments[0].billing_period == "202501"
        assert installments[23].billing_period == "202612"

    def test_purchase_on_last_day_of_month(self):
        """
        GIVEN: Purchase on last day of month
        WHEN: Generating installments
        THEN: Should handle month transitions correctly
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=15,
            payment_due_day=25,
        )
        total_amount = Money(Decimal("3000.00"), Currency.ARS)
        purchase_date = date(2025, 1, 31)

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=total_amount,
            installments_count=3,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Assert - After close day 15
        # Purchase Jan 31 (after close 15) → Feb 15 statement → period 202502
        assert installments[0].billing_period == "202502"  # Feb statement
        assert installments[1].billing_period == "202503"  # Mar statement
        assert installments[2].billing_period == "202504"  # Apr statement

    def test_different_currency_preserved(self):
        """
        GIVEN: Purchase in USD
        WHEN: Generating installments
        THEN: Currency should be preserved in all installments
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        total_amount = Money(Decimal("300.00"), Currency.USD)
        purchase_date = date(2025, 1, 5)

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=total_amount,
            installments_count=3,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Assert
        for inst in installments:
            assert inst.amount.currency == Currency.USD

    def test_very_small_amounts(self):
        """
        GIVEN: Purchase with small amount (cents) that divides properly
        WHEN: Generating installments
        THEN: Should handle properly and sum correctly
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        total_amount = Money(Decimal("10.00"), Currency.ARS)
        purchase_date = date(2025, 1, 5)

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=100,
            total_amount=total_amount,
            installments_count=3,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Assert
        # 10.00 / 3 = 3.33 per installment (rounded to cents)
        # First installment: 3.33 + 0.01 remainder = 3.34
        assert installments[0].amount.amount == Decimal("3.34")
        assert installments[1].amount.amount == Decimal("3.33")
        assert installments[2].amount.amount == Decimal("3.33")

        total_sum = sum(inst.amount.amount for inst in installments)
        assert total_sum == Decimal("10.00")

    def test_purchase_id_propagated_to_all_installments(self):
        """
        GIVEN: Purchase with specific ID
        WHEN: Generating installments
        THEN: All installments should reference the purchase_id
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
        )
        total_amount = Money(Decimal("3000.00"), Currency.ARS)
        purchase_date = date(2025, 1, 5)
        purchase_id = 999

        # Act
        installments = InstallmentGenerator.generate_installments(
            purchase_id=purchase_id,
            total_amount=total_amount,
            installments_count=3,
            purchase_date=purchase_date,
            credit_card=credit_card,
        )

        # Assert
        for inst in installments:
            assert inst.purchase_id == 999
