import pytest
from decimal import Decimal
from unittest.mock import Mock

from app.application.use_cases.get_credit_card_summary_use_case import (
    GetCreditCardSummaryUseCase,
    GetCreditCardSummaryQuery,
    CreditCardSummary,
)
from app.domain.entities.credit_card import CreditCard
from app.domain.entities.installment import Installment
from app.domain.value_objects.money import Money, Currency


@pytest.fixture
def mock_unit_of_work():
    """Mock UnitOfWork"""
    uow = Mock()
    uow.credit_cards = Mock()
    uow.installments = Mock()
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


class TestGetCreditCardSummaryUseCase:

    def test_should_return_summary_with_installments(
        self, mock_unit_of_work, mock_credit_card
    ):
        """
        GIVEN: Credit card has installments for the period
        WHEN: Execute query
        THEN: Returns summary with totals and installment list
        """
        # Arrange
        installments = [
            Installment(
                id=1,
                purchase_id=1,
                installment_number=1,
                total_installments=3,
                amount=Money(Decimal("1000.00"), Currency.ARS),
                billing_period="202501",
            ),
            Installment(
                id=2,
                purchase_id=2,
                installment_number=1,
                total_installments=1,
                amount=Money(Decimal("2000.00"), Currency.ARS),
                billing_period="202501",
            ),
        ]

        mock_unit_of_work.credit_cards.find_by_id.return_value = mock_credit_card
        mock_unit_of_work.installments.find_by_credit_card_and_period.return_value = (
            installments
        )

        query = GetCreditCardSummaryQuery(
            credit_card_id=1, user_id=10, billing_period="202501"
        )
        use_case = GetCreditCardSummaryUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(query)

        # Assert
        assert isinstance(result, CreditCardSummary)
        assert result.credit_card_id == 1
        assert result.billing_period == "202501"
        assert result.total_amount.amount == Decimal("3000.00")
        assert result.installments_count == 2
        assert len(result.installments) == 2

    def test_should_return_summary_with_zero_amount_when_no_installments(
        self, mock_unit_of_work, mock_credit_card
    ):
        """
        GIVEN: Credit card has no installments for the period
        WHEN: Execute query
        THEN: Returns summary with zero amount
        """
        # Arrange
        mock_unit_of_work.credit_cards.find_by_id.return_value = mock_credit_card
        mock_unit_of_work.installments.find_by_credit_card_and_period.return_value = []

        query = GetCreditCardSummaryQuery(
            credit_card_id=1, user_id=10, billing_period="202501"
        )
        use_case = GetCreditCardSummaryUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(query)

        # Assert
        assert result.total_amount.amount == Decimal("0")
        assert result.installments_count == 0
        assert result.installments == []

    def test_should_raise_error_when_credit_card_not_found(self, mock_unit_of_work):
        """
        GIVEN: Credit card does not exist
        WHEN: Execute query
        THEN: Raises ValueError
        """
        # Arrange
        mock_unit_of_work.credit_cards.find_by_id.return_value = None
        query = GetCreditCardSummaryQuery(
            credit_card_id=999, user_id=10, billing_period="202501"
        )
        use_case = GetCreditCardSummaryUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ValueError, match="Credit card with ID 999 not found"):
            use_case.execute(query)

    def test_should_raise_error_when_credit_card_belongs_to_different_user(
        self, mock_unit_of_work, mock_credit_card
    ):
        """
        GIVEN: Credit card belongs to different user
        WHEN: Execute query with different user_id
        THEN: Raises ValueError
        """
        # Arrange
        mock_unit_of_work.credit_cards.find_by_id.return_value = mock_credit_card
        query = GetCreditCardSummaryQuery(
            credit_card_id=1, user_id=999, billing_period="202501"  # Different user
        )
        use_case = GetCreditCardSummaryUseCase(mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ValueError, match="does not belong to user 999"):
            use_case.execute(query)
