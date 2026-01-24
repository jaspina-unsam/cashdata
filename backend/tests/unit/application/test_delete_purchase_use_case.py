import pytest
from unittest.mock import MagicMock

from app.application.use_cases.delete_purchase_use_case import (
    DeletePurchaseUseCase,
)
from app.domain.entities.purchase import Purchase
from app.domain.value_objects.money import Money, Currency


class TestDeletePurchaseUseCase:
    def test_should_delete_purchase_when_user_owns_it(self):
        # Arrange
        mock_uow = MagicMock()
        mock_purchase_repo = MagicMock()
        mock_installment_repo = MagicMock()
        mock_budget_expense_repo = MagicMock()

        mock_uow.purchases = mock_purchase_repo
        mock_uow.installments = mock_installment_repo
        mock_uow.budget_expenses = mock_budget_expense_repo

        # Mock finding the purchase
        purchase = Purchase(
            id=1,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date="2025-01-01",
            description="Test purchase",
            total_amount=Money(100.00, Currency.ARS),
            installments_count=1,
        )
        mock_purchase_repo.find_by_id.return_value = purchase

        # Mock installments and expenses
        mock_installment = MagicMock()
        mock_installment.id = 10
        mock_installment_repo.find_by_purchase_id.return_value = [mock_installment]
        mock_budget_expense_repo.find_by_installment_id.return_value = []
        mock_budget_expense_repo.find_by_purchase_id.return_value = []

        use_case = DeletePurchaseUseCase(mock_uow)

        # Act
        use_case.execute(1, 1)

        # Assert
        mock_purchase_repo.find_by_id.assert_called_once_with(1)
        mock_budget_expense_repo.find_by_installment_id.assert_called_once_with(10)
        mock_installment_repo.delete.assert_called_once_with(10)
        mock_budget_expense_repo.find_by_purchase_id.assert_called_once_with(1)
        mock_purchase_repo.delete.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()

    def test_should_raise_error_when_purchase_not_found(self):
        # Arrange
        mock_uow = MagicMock()
        mock_purchase_repo = MagicMock()
        mock_uow.purchases = mock_purchase_repo

        mock_purchase_repo.find_by_id.return_value = None

        use_case = DeletePurchaseUseCase(mock_uow)

        # Act & Assert
        with pytest.raises(ValueError, match="Purchase with ID 1 not found for user 1"):
            use_case.execute(1, 1)

        mock_purchase_repo.delete.assert_not_called()
        mock_uow.commit.assert_not_called()

    def test_should_raise_error_when_purchase_belongs_to_different_user(self):
        # Arrange
        mock_uow = MagicMock()
        mock_purchase_repo = MagicMock()
        mock_uow.purchases = mock_purchase_repo

        # Mock finding the purchase that belongs to user 2
        purchase = Purchase(
            id=1,
            user_id=2,  # Different user
            payment_method_id=1,
            category_id=1,
            purchase_date="2025-01-01",
            description="Test purchase",
            total_amount=Money(100.00, Currency.ARS),
            installments_count=1,
        )
        mock_purchase_repo.find_by_id.return_value = purchase

        use_case = DeletePurchaseUseCase(mock_uow)

        # Act & Assert
        with pytest.raises(ValueError, match="Purchase with ID 1 not found for user 1"):
            use_case.execute(1, 1)

        mock_purchase_repo.delete.assert_not_called()
        mock_uow.commit.assert_not_called()