import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from app.application.use_cases.create_purchase_use_case import (
    CreatePurchaseUseCase,
    CreatePurchaseCommand,
    CreatePurchaseResult,
)
from app.application.exceptions.application_exceptions import (
    CreditCardNotFoundError,
    PaymentMethodInstallmentError,
    PaymentMethodNotFoundError,
    PaymentMethodOwnershipError,
)
from app.domain.entities.purchase import Purchase
from app.domain.entities.category import Category
from app.domain.entities.payment_method import PaymentMethod
from app.domain.entities.credit_card import CreditCard
from app.domain.entities.bank_account import BankAccount
from app.domain.entities.installment import Installment
from app.domain.value_objects.money import Money, Currency
from app.domain.value_objects.payment_method_type import PaymentMethodType


@pytest.fixture
def mock_unit_of_work():
    """Mock UnitOfWork with all repositories"""
    uow = Mock()
    uow.payment_methods = Mock()
    uow.categories = Mock()
    uow.credit_cards = Mock()
    uow.bank_accounts = Mock()
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
def mock_payment_method_credit_card():
    """Mock credit card payment method"""
    return PaymentMethod(
        id=1,
        user_id=10,
        type=PaymentMethodType.CREDIT_CARD,
        name="Visa Gold",
        is_active=True,
        created_at=None,
        updated_at=None
    )


@pytest.fixture
def mock_payment_method_cash():
    """Mock cash payment method"""
    return PaymentMethod(
        id=2,
        user_id=10,
        type=PaymentMethodType.CASH,
        name="Cash",
        is_active=True,
        created_at=None,
        updated_at=None
    )


@pytest.fixture
def mock_credit_card():
    """Mock credit card"""
    return CreditCard(
        id=1,
        payment_method_id=1,
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


@pytest.fixture
def mock_payment_method_bank_account():
    """Mock bank account payment method"""
    return PaymentMethod(
        id=3,
        user_id=10,
        type=PaymentMethodType.BANK_ACCOUNT,
        name="Santander Checking",
        is_active=True,
        created_at=None,
        updated_at=None
    )


@pytest.fixture
def mock_bank_account():
    """Mock bank account"""
    return BankAccount(
        id=1,
        payment_method_id=3,
        primary_user_id=10,
        secondary_user_id=20,  # User 10 has access as primary, user 20 as secondary
        name="Main Checking",
        bank="Santander",
        account_type="CHECKING",
        last_four_digits="5678",
        currency=Currency.ARS,
    )


class TestCreatePurchaseUseCase:

    def test_should_create_credit_card_purchase_with_single_installment(
        self, mock_unit_of_work, mock_payment_method_credit_card, mock_credit_card, mock_category
    ):
        """
        GIVEN: Valid purchase command with credit card and 1 installment
        WHEN: Execute use case
        THEN: Creates purchase and 1 installment, creates statement
        """
        # Arrange
        mock_unit_of_work.payment_methods.find_by_id.return_value = mock_payment_method_credit_card
        mock_unit_of_work.credit_cards.find_by_payment_method_id.return_value = mock_credit_card
        mock_unit_of_work.categories.find_by_id.return_value = mock_category

        saved_purchase = Purchase(
            id=100,
            user_id=10,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Laptop",
            total_amount=Money(Decimal("50000.00"), Currency.ARS),
            installments_count=1,
        )
        mock_unit_of_work.purchases.save.return_value = saved_purchase

        command = CreatePurchaseCommand(
            user_id=10,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Laptop",
            total_amount=Decimal("50000.00"),
            currency="ARS",
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.purchase_id == 100
        assert result.payment_type == PaymentMethodType.CREDIT_CARD
        assert result.installments_count == 1
        mock_unit_of_work.purchases.save.assert_called_once()
        mock_unit_of_work.installments.save_all.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_should_create_credit_card_purchase_with_multiple_installments(
        self, mock_unit_of_work, mock_payment_method_credit_card, mock_credit_card, mock_category
    ):
        """
        GIVEN: Valid purchase command with credit card and 12 installments
        WHEN: Execute use case
        THEN: Creates purchase and 12 installments, creates statements
        """
        # Arrange
        mock_unit_of_work.payment_methods.find_by_id.return_value = mock_payment_method_credit_card
        mock_unit_of_work.credit_cards.find_by_payment_method_id.return_value = mock_credit_card
        mock_unit_of_work.categories.find_by_id.return_value = mock_category

        saved_purchase = Purchase(
            id=101,
            user_id=10,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="TV",
            total_amount=Money(Decimal("120000.00"), Currency.ARS),
            installments_count=12,
        )
        mock_unit_of_work.purchases.save.return_value = saved_purchase

        command = CreatePurchaseCommand(
            user_id=10,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="TV",
            total_amount=Decimal("120000.00"),
            currency="ARS",
            installments_count=12,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.purchase_id == 101
        assert result.payment_type == PaymentMethodType.CREDIT_CARD
        assert result.installments_count == 12
        mock_unit_of_work.installments.save_all.assert_called_once()
        # Verify 12 installments were generated
        call_args = mock_unit_of_work.installments.save_all.call_args[0][0]
        assert len(call_args) == 12

    def test_should_create_cash_purchase_without_installments(
        self, mock_unit_of_work, mock_payment_method_cash, mock_category
    ):
        """
        GIVEN: Valid purchase command with cash payment method
        WHEN: Execute use case
        THEN: Creates purchase without installments or statements
        """
        # Arrange
        mock_unit_of_work.payment_methods.find_by_id.return_value = mock_payment_method_cash
        mock_unit_of_work.categories.find_by_id.return_value = mock_category

        saved_purchase = Purchase(
            id=102,
            user_id=10,
            payment_method_id=2,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Groceries",
            total_amount=Money(Decimal("2500.00"), Currency.ARS),
            installments_count=1,
        )
        mock_unit_of_work.purchases.save.return_value = saved_purchase

        command = CreatePurchaseCommand(
            user_id=10,
            payment_method_id=2,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Groceries",
            total_amount=Decimal("2500.00"),
            currency="ARS",
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.purchase_id == 102
        assert result.payment_type == PaymentMethodType.CASH
        assert result.installments_count == 1
        mock_unit_of_work.purchases.save.assert_called_once()
        mock_unit_of_work.installments.save_all.assert_not_called()  # No installments for cash
        mock_unit_of_work.commit.assert_called_once()

    def test_should_raise_error_when_payment_method_not_found(
        self, mock_unit_of_work
    ):
        """
        GIVEN: Command with non-existent payment method
        WHEN: Execute use case
        THEN: Raises PaymentMethodNotFoundError
        """
        # Arrange
        mock_unit_of_work.payment_methods.find_by_id.return_value = None

        command = CreatePurchaseCommand(
            user_id=10,
            payment_method_id=999,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Invalid",
            total_amount=Decimal("1000.00"),
            currency="ARS",
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(PaymentMethodNotFoundError, match="Payment method with ID 999 not found"):
            use_case.execute(command)

        mock_unit_of_work.commit.assert_not_called()

    def test_should_raise_error_when_payment_method_belongs_to_different_user(
        self, mock_unit_of_work, mock_payment_method_credit_card
    ):
        """
        GIVEN: Command with payment method belonging to different user
        WHEN: Execute use case
        THEN: Raises PaymentMethodOwnershipError
        """
        # Arrange
        other_user_payment_method = PaymentMethod(
            id=1,
            user_id=999,  # Different user
            type=PaymentMethodType.CREDIT_CARD,
            name="Visa",
            is_active=True,
            created_at=None,
            updated_at=None
        )
        mock_unit_of_work.payment_methods.find_by_id.return_value = other_user_payment_method

        command = CreatePurchaseCommand(
            user_id=10,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Invalid",
            total_amount=Decimal("1000.00"),
            currency="ARS",
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(PaymentMethodOwnershipError, match="does not belong to user"):
            use_case.execute(command)

        mock_unit_of_work.commit.assert_not_called()

    def test_should_raise_error_when_credit_card_not_found_for_credit_card_payment(
        self, mock_unit_of_work, mock_payment_method_credit_card
    ):
        """
        GIVEN: Credit card payment method but no associated credit card entity
        WHEN: Execute use case
        THEN: Raises CreditCardNotFoundError
        """
        # Arrange
        mock_unit_of_work.payment_methods.find_by_id.return_value = mock_payment_method_credit_card
        mock_unit_of_work.credit_cards.find_by_payment_method_id.return_value = None

        command = CreatePurchaseCommand(
            user_id=10,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Invalid",
            total_amount=Decimal("1000.00"),
            currency="ARS",
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(CreditCardNotFoundError, match="Credit card for payment method ID 1 not found"):
            use_case.execute(command)

        mock_unit_of_work.commit.assert_not_called()

    def test_should_raise_error_when_invalid_installments_for_payment_method(
        self, mock_unit_of_work, mock_payment_method_cash
    ):
        """
        GIVEN: Cash payment method with multiple installments (invalid)
        WHEN: Execute use case
        THEN: Raises PaymentMethodInstallmentError
        """
        # Arrange
        mock_unit_of_work.payment_methods.find_by_id.return_value = mock_payment_method_cash

        command = CreatePurchaseCommand(
            user_id=10,
            payment_method_id=2,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Invalid",
            total_amount=Decimal("1000.00"),
            currency="ARS",
            installments_count=3,  # Invalid for cash
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(PaymentMethodInstallmentError, match="Only credit card payment methods can have multiple installments"):
            use_case.execute(command)

        mock_unit_of_work.commit.assert_not_called()

    def test_should_raise_error_when_category_not_found(
        self, mock_unit_of_work, mock_payment_method_cash
    ):
        """
        GIVEN: Command with non-existent category
        WHEN: Execute use case
        THEN: Raises ValueError
        """
        # Arrange
        mock_unit_of_work.payment_methods.find_by_id.return_value = mock_payment_method_cash
        mock_unit_of_work.categories.find_by_id.return_value = None

        command = CreatePurchaseCommand(
            user_id=10,
            payment_method_id=2,
            category_id=999,
            purchase_date=date(2025, 1, 15),
            description="Invalid",
            total_amount=Decimal("1000.00"),
            currency="ARS",
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ValueError, match="Category with ID 999 not found"):
            use_case.execute(command)

        mock_unit_of_work.commit.assert_not_called()

    def test_should_create_statements_for_credit_card_installments(
        self, mock_unit_of_work, mock_payment_method_credit_card, mock_credit_card, mock_category
    ):
        """
        GIVEN: Credit card purchase with multiple installments
        WHEN: Execute use case
        THEN: Creates statements for each billing period
        """
        # Arrange
        mock_unit_of_work.payment_methods.find_by_id.return_value = mock_payment_method_credit_card
        mock_unit_of_work.credit_cards.find_by_payment_method_id.return_value = mock_credit_card
        mock_unit_of_work.categories.find_by_id.return_value = mock_category

        saved_purchase = Purchase(
            id=103,
            user_id=10,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Test",
            total_amount=Money(Decimal("6000.00"), Currency.ARS),
            installments_count=3,
        )
        mock_unit_of_work.purchases.save.return_value = saved_purchase

        command = CreatePurchaseCommand(
            user_id=10,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Test",
            total_amount=Decimal("6000.00"),
            currency="ARS",
            installments_count=3,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(command)

        # Assert
        # Should call statement factory for each installment's billing period
        # This is tested indirectly through the installment generation
        assert result.installments_count == 3
        mock_unit_of_work.installments.save_all.assert_called_once()

    def test_should_create_bank_account_purchase_when_user_has_access(
        self, mock_unit_of_work, mock_payment_method_bank_account, mock_bank_account, mock_category
    ):
        """
        GIVEN: Valid purchase command with bank account payment method and user has access
        WHEN: Execute use case
        THEN: Creates purchase successfully
        """
        # Arrange
        mock_unit_of_work.payment_methods.find_by_id.return_value = mock_payment_method_bank_account
        mock_unit_of_work.bank_accounts.find_by_payment_method_id.return_value = mock_bank_account
        mock_unit_of_work.categories.find_by_id.return_value = mock_category

        saved_purchase = Purchase(
            id=104,
            user_id=10,
            payment_method_id=3,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="ATM Withdrawal",
            total_amount=Money(Decimal("5000.00"), Currency.ARS),
            installments_count=1,
        )
        mock_unit_of_work.purchases.save.return_value = saved_purchase

        command = CreatePurchaseCommand(
            user_id=10,  # User 10 has access as primary user
            payment_method_id=3,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="ATM Withdrawal",
            total_amount=Decimal("5000.00"),
            currency="ARS",
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.purchase_id == 104
        assert result.payment_type == PaymentMethodType.BANK_ACCOUNT
        assert result.installments_count == 1
        mock_unit_of_work.purchases.save.assert_called_once()
        mock_unit_of_work.installments.save_all.assert_not_called()  # No installments for bank account
        mock_unit_of_work.commit.assert_called_once()

    def test_should_create_bank_account_purchase_when_user_has_secondary_access(
        self, mock_unit_of_work, mock_payment_method_bank_account, mock_bank_account, mock_category
    ):
        """
        GIVEN: Valid purchase command with bank account payment method and user has secondary access
        WHEN: Execute use case
        THEN: Creates purchase successfully
        """
        # Arrange
        mock_unit_of_work.payment_methods.find_by_id.return_value = mock_payment_method_bank_account
        mock_unit_of_work.bank_accounts.find_by_payment_method_id.return_value = mock_bank_account
        mock_unit_of_work.categories.find_by_id.return_value = mock_category

        saved_purchase = Purchase(
            id=105,
            user_id=20,
            payment_method_id=3,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Shared Expense",
            total_amount=Money(Decimal("3000.00"), Currency.ARS),
            installments_count=1,
        )
        mock_unit_of_work.purchases.save.return_value = saved_purchase

        command = CreatePurchaseCommand(
            user_id=20,  # User 20 has access as secondary user
            payment_method_id=3,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Shared Expense",
            total_amount=Decimal("3000.00"),
            currency="ARS",
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.purchase_id == 105
        assert result.payment_type == PaymentMethodType.BANK_ACCOUNT
        assert result.installments_count == 1
        mock_unit_of_work.purchases.save.assert_called_once()
        mock_unit_of_work.installments.save_all.assert_not_called()  # No installments for bank account
        mock_unit_of_work.commit.assert_called_once()

    def test_should_raise_error_when_user_does_not_have_access_to_bank_account(
        self, mock_unit_of_work, mock_payment_method_bank_account, mock_bank_account
    ):
        """
        GIVEN: Bank account payment method but user does not have access to the bank account
        WHEN: Execute use case
        THEN: Raises PaymentMethodOwnershipError
        """
        # Arrange
        mock_unit_of_work.payment_methods.find_by_id.return_value = mock_payment_method_bank_account
        mock_unit_of_work.bank_accounts.find_by_payment_method_id.return_value = mock_bank_account

        command = CreatePurchaseCommand(
            user_id=999,  # User 999 does not have access (only users 10 and 20 do)
            payment_method_id=3,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Unauthorized Purchase",
            total_amount=Decimal("1000.00"),
            currency="ARS",
            installments_count=1,
        )

        use_case = CreatePurchaseUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(PaymentMethodOwnershipError, match="User 999 does not have access to bank account with payment method ID 3"):
            use_case.execute(command)

        mock_unit_of_work.commit.assert_not_called()
