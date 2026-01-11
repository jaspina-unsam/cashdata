import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from app.application.use_cases.get_purchase_by_id_use_case import (
    GetPurchaseByIdUseCase,
    GetPurchaseByIdQuery,
)
from app.domain.entities.purchase import Purchase
from app.domain.value_objects.money import Money, Currency


@pytest.fixture
def mock_unit_of_work():
    """Mock UnitOfWork"""
    uow = Mock()
    uow.purchases = Mock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


@pytest.fixture
def sample_purchase():
    """Sample purchase for tests"""
    return Purchase(
        id=1,
        user_id=10,
        payment_method_id=1,
        category_id=1,
        purchase_date=date(2025, 1, 15),
        description="Laptop",
        total_amount=Money(Decimal("50000.00"), Currency.ARS),
        installments_count=12,
    )


class TestGetPurchaseByIdUseCase:

    def test_should_return_purchase_when_found_and_belongs_to_user(
        self, mock_unit_of_work, sample_purchase
    ):
        """
        GIVEN: Purchase exists and belongs to user
        WHEN: Execute query
        THEN: Returns purchase
        """
        # Arrange
        mock_unit_of_work.purchases.find_by_id.return_value = sample_purchase
        query = GetPurchaseByIdQuery(purchase_id=1, user_id=10)
        use_case = GetPurchaseByIdUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(query)

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.user_id == 10
        mock_unit_of_work.purchases.find_by_id.assert_called_once_with(1)

    def test_should_return_none_when_purchase_not_found(self, mock_unit_of_work):
        """
        GIVEN: Purchase does not exist
        WHEN: Execute query
        THEN: Returns None
        """
        # Arrange
        mock_unit_of_work.purchases.find_by_id.return_value = None
        query = GetPurchaseByIdQuery(purchase_id=999, user_id=10)
        use_case = GetPurchaseByIdUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(query)

        # Assert
        assert result is None

    def test_should_return_none_when_purchase_belongs_to_different_user(
        self, mock_unit_of_work, sample_purchase
    ):
        """
        GIVEN: Purchase exists but belongs to different user
        WHEN: Execute query with different user_id
        THEN: Returns None (authorization check)
        """
        # Arrange
        mock_unit_of_work.purchases.find_by_id.return_value = sample_purchase
        query = GetPurchaseByIdQuery(purchase_id=1, user_id=999)  # Different user
        use_case = GetPurchaseByIdUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(query)

        # Assert
        assert result is None
