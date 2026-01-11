import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from app.application.use_cases.list_purchases_by_user_use_case import (
    ListPurchasesByUserUseCase,
    ListPurchasesByUserQuery,
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


class TestListPurchasesByUserUseCase:

    def test_should_return_all_purchases_for_user(self, mock_unit_of_work):
        """
        GIVEN: User has multiple purchases
        WHEN: Execute query
        THEN: Returns all purchases sorted by date descending
        """
        # Arrange
        purchases = [
            Purchase(
                id=1,
                user_id=10,
                payment_method_id=1,
                category_id=1,
                purchase_date=date(2025, 1, 10),
                description="Old",
                total_amount=Money(Decimal("1000.00"), Currency.ARS),
                installments_count=1,
            ),
            Purchase(
                id=2,
                user_id=10,
                payment_method_id=1,
                category_id=1,
                purchase_date=date(2025, 1, 20),
                description="Recent",
                total_amount=Money(Decimal("2000.00"), Currency.ARS),
                installments_count=1,
            ),
            Purchase(
                id=3,
                user_id=10,
                payment_method_id=1,
                category_id=1,
                purchase_date=date(2025, 1, 15),
                description="Middle",
                total_amount=Money(Decimal("1500.00"), Currency.ARS),
                installments_count=1,
            ),
        ]
        mock_unit_of_work.purchases.find_by_user_id.return_value = purchases
        query = ListPurchasesByUserQuery(user_id=10)
        use_case = ListPurchasesByUserUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(query)

        # Assert
        assert len(result) == 3
        # Should be sorted by date descending
        assert result[0].purchase_date == date(2025, 1, 20)
        assert result[1].purchase_date == date(2025, 1, 15)
        assert result[2].purchase_date == date(2025, 1, 10)
        mock_unit_of_work.purchases.find_by_user_id.assert_called_once_with(10)

    def test_should_return_empty_list_when_user_has_no_purchases(
        self, mock_unit_of_work
    ):
        """
        GIVEN: User has no purchases
        WHEN: Execute query
        THEN: Returns empty list
        """
        # Arrange
        mock_unit_of_work.purchases.find_by_user_id.return_value = []
        query = ListPurchasesByUserQuery(user_id=10)
        use_case = ListPurchasesByUserUseCase(mock_unit_of_work)

        # Act
        result = use_case.execute(query)

        # Assert
        assert result == []
