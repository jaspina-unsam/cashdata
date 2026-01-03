import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from cashdata.application.use_cases.create_purchase_use_case import (
    CreatePurchaseUseCase,
    CreatePurchaseCommand,
    CreatePurchaseResult,
)
from cashdata.domain.entities.purchase import Purchase
from cashdata.domain.entities.category import Category
from cashdata.domain.entities.credit_card import CreditCard
from cashdata.domain.entities.installment import Installment
from cashdata.domain.value_objects.money import Money, Currency


@pytest.fixture
def mock_unit_of_work():
    """Mock UnitOfWork with all repositories"""
    uow = Mock()
    uow.categories = Mock()
    uow.credit_cards = Mock()
    uow.purchases = Mock()
    uow.installments = Mock()
    uow.monthly_statements = Mock()

    # Mock monthly_statements to return empty list (no existing statements)
    uow.monthly_statements.find_by_credit_card_id.return_value = []

    # Make context manager work
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)

    return uow


@pytest.fixture
def mock_credit_card():
    """Mock credit card"""
    return CreditCard(
        id=1,
        user_id=10,
        name="Visa",
        bank="HSBC",
        last_four_digits="1234",
        billing_close_day=10,
        payment_due_day=20,
        credit_limit=None,
    )


@pytest.fixture
def mock_category():
    """Mock category"""
    return Category(id=1, name="Electronics", color="#FF5733", icon="laptop")


class TestCreatePurchaseUseCase:

    def test_should_create_purchase_with_single_installment(
        self, mock_unit_of_work, mock_credit_card, mock_category
    ):
        """
        GIVEN: Valid purchase command with 1 installment
        WHEN: Execute use case
        THEN: Creates purchase and 1 installment
        """
        # Arrange
        mock_unit_of_work.credit_cards.find_by_id.return_value = mock_credit_card
        mock_unit_of_work.categories.find_by_id.return_value = mock_category

        saved_purchase = Purchase(
            id=100,
            user_id=10,
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Laptop",
            total_amount=Money(Decimal("50000.00"), Currency.ARS),
            installments_count=1,
        )
        mock_unit_of_work.purchases.save.return_value = saved_purchase

        command = CreatePurchaseCommand(
            user_id=10,
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Laptop",
            total_amount=Decimal("50000.00"),
            currency=Currency.ARS,
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.purchase_id == 100
        assert result.installments_count == 1
        mock_unit_of_work.purchases.save.assert_called_once()
        mock_unit_of_work.installments.save_all.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_should_create_purchase_with_multiple_installments(
        self, mock_unit_of_work, mock_credit_card, mock_category
    ):
        """
        GIVEN: Valid purchase command with 12 installments
        WHEN: Execute use case
        THEN: Creates purchase and 12 installments
        """
        # Arrange
        mock_unit_of_work.credit_cards.find_by_id.return_value = mock_credit_card
        mock_unit_of_work.categories.find_by_id.return_value = mock_category

        saved_purchase = Purchase(
            id=101,
            user_id=10,
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="TV",
            total_amount=Money(Decimal("120000.00"), Currency.ARS),
            installments_count=12,
        )
        mock_unit_of_work.purchases.save.return_value = saved_purchase

        command = CreatePurchaseCommand(
            user_id=10,
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="TV",
            total_amount=Decimal("120000.00"),
            currency=Currency.ARS,
            installments_count=12,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.purchase_id == 101
        assert result.installments_count == 12
        mock_unit_of_work.installments.save_all.assert_called_once()
        # Verify 12 installments were generated
        call_args = mock_unit_of_work.installments.save_all.call_args[0][0]
        assert len(call_args) == 12

    def test_should_raise_error_when_credit_card_not_found(
        self, mock_unit_of_work, mock_category
    ):
        """
        GIVEN: Command with non-existent credit card
        WHEN: Execute use case
        THEN: Raises ValueError
        """
        # Arrange
        mock_unit_of_work.credit_cards.find_by_id.return_value = None
        mock_unit_of_work.categories.find_by_id.return_value = mock_category

        command = CreatePurchaseCommand(
            user_id=10,
            credit_card_id=999,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Invalid",
            total_amount=Decimal("1000.00"),
            currency=Currency.ARS,
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ValueError, match="Credit card with ID 999 not found"):
            use_case.execute(command)

        mock_unit_of_work.commit.assert_not_called()

    def test_should_raise_error_when_credit_card_belongs_to_different_user(
        self, mock_unit_of_work, mock_category
    ):
        """
        GIVEN: Command with credit card belonging to different user
        WHEN: Execute use case
        THEN: Raises ValueError
        """
        # Arrange
        other_user_card = CreditCard(
            id=1,
            user_id=999,  # Different user
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
            credit_limit=None,
        )
        mock_unit_of_work.credit_cards.find_by_id.return_value = other_user_card
        mock_unit_of_work.categories.find_by_id.return_value = mock_category

        command = CreatePurchaseCommand(
            user_id=10,
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Invalid",
            total_amount=Decimal("1000.00"),
            currency=Currency.ARS,
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ValueError, match="does not belong to user"):
            use_case.execute(command)

        mock_unit_of_work.commit.assert_not_called()

    def test_should_raise_error_when_category_not_found(
        self, mock_unit_of_work, mock_credit_card
    ):
        """
        GIVEN: Command with non-existent category
        WHEN: Execute use case
        THEN: Raises ValueError
        """
        # Arrange
        mock_unit_of_work.credit_cards.find_by_id.return_value = mock_credit_card
        mock_unit_of_work.categories.find_by_id.return_value = None

        command = CreatePurchaseCommand(
            user_id=10,
            credit_card_id=1,
            category_id=999,
            purchase_date=date(2025, 1, 15),
            description="Invalid",
            total_amount=Decimal("1000.00"),
            currency=Currency.ARS,
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ValueError, match="Category with ID 999 not found"):
            use_case.execute(command)

        mock_unit_of_work.commit.assert_not_called()
