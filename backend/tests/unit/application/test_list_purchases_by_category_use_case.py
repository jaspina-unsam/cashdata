import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from cashdata.application.use_cases.list_purchases_by_category_use_case import (
    ListPurchasesByCategoryUseCase,
    ListPurchasesByCategoryQuery,
)
from cashdata.domain.entities.purchase import Purchase
from cashdata.domain.value_objects.money import Money, Currency


@pytest.fixture
def mock_unit_of_work():
    uow = Mock()
    uow.purchases = Mock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


class TestListPurchasesByCategoryUseCase:
    
    def test_should_return_purchases_for_category_sorted_by_date(self, mock_unit_of_work):
        """
        GIVEN: User has purchases in multiple categories
        WHEN: Execute query for specific category
        THEN: Returns only purchases for that category, sorted by date
        """
        # Arrange
        all_purchases = [
            Purchase(
                id=1, user_id=10, credit_card_id=1, category_id=1,
                purchase_date=date(2025, 1, 10), description="Old Electronics",
                total_amount=Money(Decimal("1000.00"), Currency.ARS), installments_count=1
            ),
            Purchase(
                id=2, user_id=10, credit_card_id=1, category_id=2,  # Different category
                purchase_date=date(2025, 1, 15), description="Food",
                total_amount=Money(Decimal("500.00"), Currency.ARS), installments_count=1
            ),
            Purchase(
                id=3, user_id=10, credit_card_id=1, category_id=1,
                purchase_date=date(2025, 1, 20), description="Recent Electronics",
                total_amount=Money(Decimal("2000.00"), Currency.ARS), installments_count=1
            ),
        ]
        mock_unit_of_work.purchases.find_by_user_id.return_value = all_purchases
        
        query = ListPurchasesByCategoryQuery(category_id=1, user_id=10)
        use_case = ListPurchasesByCategoryUseCase(mock_unit_of_work)
        
        # Act
        result = use_case.execute(query)
        
        # Assert
        assert len(result) == 2
        assert result[0].id == 3  # Most recent first
        assert result[1].id == 1
        assert all(p.category_id == 1 for p in result)
    
    def test_should_return_empty_list_when_no_purchases_in_category(self, mock_unit_of_work):
        """
        GIVEN: User has purchases but none in specified category
        WHEN: Execute query
        THEN: Returns empty list
        """
        # Arrange
        all_purchases = [
            Purchase(
                id=1, user_id=10, credit_card_id=1, category_id=2,
                purchase_date=date(2025, 1, 10), description="Food",
                total_amount=Money(Decimal("500.00"), Currency.ARS), installments_count=1
            ),
        ]
        mock_unit_of_work.purchases.find_by_user_id.return_value = all_purchases
        
        query = ListPurchasesByCategoryQuery(category_id=1, user_id=10)
        use_case = ListPurchasesByCategoryUseCase(mock_unit_of_work)
        
        # Act
        result = use_case.execute(query)
        
        # Assert
        assert result == []
