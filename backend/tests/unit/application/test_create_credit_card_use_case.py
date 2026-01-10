import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from app.application.use_cases.create_credit_card_use_case import (
    CreateCreditCardUseCase,
    CreateCreditCardQuery,
)
from app.domain.entities.credit_card import CreditCard
from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.domain.value_objects.money import Money, Currency


class TestCreateCreditCardUseCase:
    """Unit tests for CreateCreditCardUseCase."""

    def setup_method(self):
        """Setup test fixtures."""
        self.mock_uow = Mock()
        self.mock_payment_methods_repo = Mock()
        self.mock_credit_cards_repo = Mock()

        # Configure UoW mock
        self.mock_uow.__enter__ = Mock(return_value=self.mock_uow)
        self.mock_uow.__exit__ = Mock(return_value=None)
        self.mock_uow.payment_methods = self.mock_payment_methods_repo
        self.mock_uow.credit_cards = self.mock_credit_cards_repo
        self.mock_uow.commit = Mock()

        self.use_case = CreateCreditCardUseCase(self.mock_uow)

    def test_execute_creates_payment_method_and_credit_card_successfully(self):
        """Test successful creation of payment method and credit card."""
        # Arrange
        query = CreateCreditCardQuery(
            user_id=1,
            name="Visa Gold",
            bank="Test Bank",
            last_four_digits="1234",
            billing_close_day=15,
            payment_due_day=10,
            credit_limit_amount=Decimal('50000.0'),
            credit_limit_currency=Currency.ARS
        )

        # Mock payment method creation
        mock_payment_method = PaymentMethod(
            id=100,
            user_id=1,
            type=PaymentMethodType.CREDIT_CARD,
            name="Visa Gold",
            is_active=True,
            created_at=None,
            updated_at=None
        )
        self.mock_payment_methods_repo.save.return_value = mock_payment_method

        # Mock credit card creation
        mock_credit_card = CreditCard(
            id=200,
            payment_method_id=100,
            user_id=1,
            name="Visa Gold",
            bank="Test Bank",
            last_four_digits="1234",
            billing_close_day=15,
            payment_due_day=10,
            credit_limit=Money(Decimal('50000.0'), Currency.ARS)
        )
        self.mock_credit_cards_repo.save.return_value = mock_credit_card

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == mock_credit_card

        # Verify payment method was created
        self.mock_payment_methods_repo.save.assert_called_once()
        pm_call_args = self.mock_payment_methods_repo.save.call_args[0][0]
        assert isinstance(pm_call_args, PaymentMethod)
        assert pm_call_args.user_id == 1
        assert pm_call_args.type == PaymentMethodType.CREDIT_CARD
        assert pm_call_args.name == "Visa Gold"

        # Verify credit card was created
        self.mock_credit_cards_repo.save.assert_called_once()
        cc_call_args = self.mock_credit_cards_repo.save.call_args[0][0]
        assert isinstance(cc_call_args, CreditCard)
        assert cc_call_args.user_id == 1
        assert cc_call_args.payment_method_id == 100  # From saved payment method
        assert cc_call_args.name == "Visa Gold"
        assert cc_call_args.bank == "Test Bank"
        assert cc_call_args.last_four_digits == "1234"
        assert cc_call_args.billing_close_day == 15
        assert cc_call_args.payment_due_day == 10
        assert cc_call_args.credit_limit == Money(Decimal('50000.0'), Currency.ARS)

        # Verify transaction was committed
        self.mock_uow.commit.assert_called_once()

    def test_execute_handles_credit_limit_none(self):
        """Test creation with no credit limit."""
        # Arrange
        query = CreateCreditCardQuery(
            user_id=2,
            name="Mastercard",
            bank="Test Bank",
            last_four_digits="5678",
            billing_close_day=20,
            payment_due_day=15,
            credit_limit_amount=None,
            credit_limit_currency=None
        )

        # Mock payment method
        mock_payment_method = PaymentMethod(
            id=101,
            user_id=2,
            type=PaymentMethodType.CREDIT_CARD,
            name="Mastercard",
            is_active=True,
            created_at=None,
            updated_at=None
        )
        self.mock_payment_methods_repo.save.return_value = mock_payment_method

        # Mock credit card with no limit
        mock_credit_card = CreditCard(
            id=201,
            payment_method_id=101,
            user_id=2,
            name="Mastercard",
            bank="Test Bank",
            last_four_digits="5678",
            billing_close_day=20,
            payment_due_day=15,
            credit_limit=None
        )
        self.mock_credit_cards_repo.save.return_value = mock_credit_card

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == mock_credit_card
        cc_call_args = self.mock_credit_cards_repo.save.call_args[0][0]
        assert cc_call_args.credit_limit is None

    def test_execute_uses_context_manager_properly(self):
        """Test that Unit of Work context manager is used correctly."""
        # Arrange
        query = CreateCreditCardQuery(
            user_id=1,
            name="Test Card",
            bank="Test Bank",
            last_four_digits="9999",
            billing_close_day=5,
            payment_due_day=25,
            credit_limit_amount=Decimal('10000.0'),
            credit_limit_currency=Currency.ARS
        )

        mock_payment_method = PaymentMethod(
            id=102,
            user_id=1,
            type=PaymentMethodType.CREDIT_CARD,
            name="Test Card",
            is_active=True,
            created_at=None,
            updated_at=None
        )
        self.mock_payment_methods_repo.save.return_value = mock_payment_method

        mock_credit_card = CreditCard(
            id=202,
            payment_method_id=102,
            user_id=1,
            name="Test Card",
            bank="Test Bank",
            last_four_digits="9999",
            billing_close_day=5,
            payment_due_day=25,
            credit_limit=Money(Decimal('10000.0'), Currency.ARS)
        )
        self.mock_credit_cards_repo.save.return_value = mock_credit_card

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == mock_credit_card

        # Verify context manager usage
        self.mock_uow.__enter__.assert_called_once()
        self.mock_uow.__exit__.assert_called_once()

        # Verify operations happened in correct order
        call_order = [
            self.mock_uow.__enter__,
            self.mock_payment_methods_repo.save,
            self.mock_credit_cards_repo.save,
            self.mock_uow.commit,
            self.mock_uow.__exit__
        ]

        # Check that all calls were made (order verification would require more complex mocking)
        assert self.mock_payment_methods_repo.save.called
        assert self.mock_credit_cards_repo.save.called
        assert self.mock_uow.commit.called

    def test_execute_handles_repository_errors(self):
        """Test that repository errors are propagated."""
        # Arrange
        query = CreateCreditCardQuery(
            user_id=1,
            name="Error Card",
            bank="Error Bank",
            last_four_digits="0000",
            billing_close_day=10,
            payment_due_day=5,
            credit_limit_amount=Decimal('5000.0'),
            credit_limit_currency=Currency.ARS
        )

        # Simulate repository error
        self.mock_payment_methods_repo.save.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            self.use_case.execute(query)

        # Verify rollback (context manager exit should still be called)
        self.mock_uow.__enter__.assert_called_once()
        self.mock_uow.__exit__.assert_called_once()
        # commit should not be called due to error
        self.mock_uow.commit.assert_not_called()

    def test_execute_validates_payment_method_creation(self):
        """Test that payment method is created with correct attributes."""
        # Arrange
        query = CreateCreditCardQuery(
            user_id=123,
            name="Premium Card",
            bank="Premium Bank",
            last_four_digits="1111",
            billing_close_day=25,
            payment_due_day=20,
            credit_limit_amount=Decimal('100000.0'),
            credit_limit_currency=Currency.ARS
        )

        mock_payment_method = PaymentMethod(
            id=103,
            user_id=123,
            type=PaymentMethodType.CREDIT_CARD,
            name="Premium Card",
            is_active=True,
            created_at=None,
            updated_at=None
        )
        self.mock_payment_methods_repo.save.return_value = mock_payment_method

        mock_credit_card = CreditCard(
            id=203,
            payment_method_id=103,
            user_id=123,
            name="Premium Card",
            bank="Premium Bank",
            last_four_digits="1111",
            billing_close_day=25,
            payment_due_day=20,
            credit_limit=Money(Decimal('100000.0'), Currency.ARS)
        )
        self.mock_credit_cards_repo.save.return_value = mock_credit_card

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == mock_credit_card

        # Verify payment method attributes
        pm_call_args = self.mock_payment_methods_repo.save.call_args[0][0]
        assert pm_call_args.id is None
        assert pm_call_args.user_id == 123
        assert pm_call_args.type == PaymentMethodType.CREDIT_CARD
        assert pm_call_args.name == "Premium Card"
        assert pm_call_args.is_active is True

        # Verify credit card attributes
        cc_call_args = self.mock_credit_cards_repo.save.call_args[0][0]
        assert cc_call_args.payment_method_id == 103
        assert cc_call_args.bank == "Premium Bank"
        assert cc_call_args.last_four_digits == "1111"
        assert cc_call_args.billing_close_day == 25
        assert cc_call_args.payment_due_day == 20

    def test_execute_links_credit_card_to_payment_method(self):
        """Test that credit card is properly linked to its payment method."""
        # Arrange
        query = CreateCreditCardQuery(
            user_id=5,
            name="Linked Card",
            bank="Linked Bank",
            last_four_digits="2222",
            billing_close_day=12,
            payment_due_day=7,
            credit_limit_amount=Decimal('25000.0'),
            credit_limit_currency=Currency.ARS
        )

        # Payment method gets ID 104
        mock_payment_method = PaymentMethod(
            id=104,
            user_id=5,
            type=PaymentMethodType.CREDIT_CARD,
            name="Linked Card",
            is_active=True,
            created_at=None,
            updated_at=None
        )
        self.mock_payment_methods_repo.save.return_value = mock_payment_method

        mock_credit_card = CreditCard(
            id=204,
            payment_method_id=104,  # Should match payment method ID
            user_id=5,
            name="Linked Card",
            bank="Linked Bank",
            last_four_digits="2222",
            billing_close_day=12,
            payment_due_day=7,
            credit_limit=Money(Decimal('25000.0'), Currency.ARS)
        )
        self.mock_credit_cards_repo.save.return_value = mock_credit_card

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == mock_credit_card

        # Verify the linkage
        cc_call_args = self.mock_credit_cards_repo.save.call_args[0][0]
        assert cc_call_args.payment_method_id == 104  # From the saved payment method
        assert cc_call_args.user_id == 5


class TestCreateCreditCardQuery:
    """Tests for CreateCreditCardQuery dataclass."""

    def test_query_creation_valid(self):
        """Test creating a valid query."""
        query = CreateCreditCardQuery(
            user_id=1,
            name="Test Card",
            bank="Test Bank",
            last_four_digits="1234",
            billing_close_day=15,
            payment_due_day=10,
            credit_limit_amount=Decimal('10000.0'),
            credit_limit_currency=Currency.ARS
        )

        assert query.user_id == 1
        assert query.name == "Test Card"
        assert query.bank == "Test Bank"
        assert query.last_four_digits == "1234"
        assert query.billing_close_day == 15
        assert query.payment_due_day == 10
        assert query.credit_limit_amount == Decimal('10000.0')
        assert query.credit_limit_currency == Currency.ARS

    def test_query_is_frozen(self):
        """Test that query is immutable (frozen dataclass)."""
        query = CreateCreditCardQuery(
            user_id=1,
            name="Test Card",
            bank="Test Bank",
            last_four_digits="1234",
            billing_close_day=15,
            payment_due_day=10
        )

        with pytest.raises(AttributeError):
            query.user_id = 2

    def test_query_equality(self):
        """Test query equality."""
        query1 = CreateCreditCardQuery(
            user_id=1,
            name="Test Card",
            bank="Test Bank",
            last_four_digits="1234",
            billing_close_day=15,
            payment_due_day=10,
            credit_limit_amount=Decimal('5000.0'),
            credit_limit_currency=Currency.ARS
        )

        query2 = CreateCreditCardQuery(
            user_id=1,
            name="Test Card",
            bank="Test Bank",
            last_four_digits="1234",
            billing_close_day=15,
            payment_due_day=10,
            credit_limit_amount=Decimal('5000.0'),
            credit_limit_currency=Currency.ARS
        )

        query3 = CreateCreditCardQuery(
            user_id=2,  # Different
            name="Test Card",
            bank="Test Bank",
            last_four_digits="1234",
            billing_close_day=15,
            payment_due_day=10
        )

        assert query1 == query2
        assert query1 != query3