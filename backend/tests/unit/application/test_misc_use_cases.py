import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from app.application.use_cases.list_installments_by_purchase_use_case import (
    ListInstallmentsByPurchaseUseCase,
    ListInstallmentsByPurchaseQuery,
)
from app.application.use_cases.list_purchases_by_credit_card_use_case import (
    ListPurchasesByCreditCardUseCase,
    ListPurchasesByCreditCardQuery,
)
from app.application.use_cases.list_purchases_by_date_range_use_case import (
    ListPurchasesByDateRangeUseCase,
    ListPurchasesByDateRangeQuery,
)
from app.application.use_cases.list_credit_cards_by_user_use_case import (
    ListCreditCardsByUserUseCase,
    ListCreditCardsByUserQuery,
)
from app.domain.entities.purchase import Purchase
from app.domain.entities.installment import Installment
from app.domain.entities.credit_card import CreditCard
from app.domain.value_objects.money import Money, Currency


@pytest.fixture
def mock_unit_of_work():
    uow = Mock()
    uow.purchases = Mock()
    uow.installments = Mock()
    uow.credit_cards = Mock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


class TestListInstallmentsByPurchaseUseCase:

    def test_should_return_installments_sorted_by_number(self, mock_unit_of_work):
        """
        GIVEN: Purchase with multiple installments
        WHEN: Execute query
        THEN: Returns installments sorted by number
        """
        purchase = Purchase(
            id=1,
            user_id=10,
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="TV",
            total_amount=Money(Decimal("30000.00"), Currency.ARS),
            installments_count=3,
        )
        installments = [
            Installment(
                id=3,
                purchase_id=1,
                installment_number=3,
                total_installments=3,
                amount=Money(Decimal("10000.00"), Currency.ARS),
                billing_period="202504",
                manually_assigned_statement_id=None
            ),
            Installment(
                id=1,
                purchase_id=1,
                installment_number=1,
                total_installments=3,
                amount=Money(Decimal("10000.00"), Currency.ARS),
                billing_period="202502",
                manually_assigned_statement_id=None
            ),
            Installment(
                id=2,
                purchase_id=1,
                installment_number=2,
                total_installments=3,
                amount=Money(Decimal("10000.00"), Currency.ARS),
                billing_period="202503",
                manually_assigned_statement_id=None
            ),
        ]

        mock_unit_of_work.purchases.find_by_id.return_value = purchase
        mock_unit_of_work.installments.find_by_purchase_id.return_value = installments

        query = ListInstallmentsByPurchaseQuery(purchase_id=1, user_id=10)
        use_case = ListInstallmentsByPurchaseUseCase(mock_unit_of_work)

        result = use_case.execute(query)

        assert len(result) == 3
        assert result[0].installment_number == 1
        assert result[1].installment_number == 2
        assert result[2].installment_number == 3

    def test_should_raise_error_when_purchase_not_found(self, mock_unit_of_work):
        """
        GIVEN: Non-existent purchase
        WHEN: Execute query
        THEN: Raises ValueError
        """
        mock_unit_of_work.purchases.find_by_id.return_value = None

        query = ListInstallmentsByPurchaseQuery(purchase_id=999, user_id=10)
        use_case = ListInstallmentsByPurchaseUseCase(mock_unit_of_work)

        with pytest.raises(ValueError, match="Purchase with ID 999 not found"):
            use_case.execute(query)


class TestListPurchasesByCreditCardUseCase:

    def test_should_return_purchases_sorted_by_date(self, mock_unit_of_work):
        """
        GIVEN: Credit card with multiple purchases
        WHEN: Execute query
        THEN: Returns purchases sorted by date descending
        """
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
            credit_limit=None,
        )
        purchases = [
            Purchase(
                id=1,
                user_id=10,
                credit_card_id=1,
                category_id=1,
                purchase_date=date(2025, 1, 10),
                description="Old",
                total_amount=Money(Decimal("1000.00"), Currency.ARS),
                installments_count=1,
            ),
            Purchase(
                id=2,
                user_id=10,
                credit_card_id=1,
                category_id=1,
                purchase_date=date(2025, 1, 20),
                description="Recent",
                total_amount=Money(Decimal("2000.00"), Currency.ARS),
                installments_count=1,
            ),
        ]

        mock_unit_of_work.credit_cards.find_by_id.return_value = credit_card
        mock_unit_of_work.purchases.find_by_credit_card_id.return_value = purchases

        query = ListPurchasesByCreditCardQuery(credit_card_id=1, user_id=10)
        use_case = ListPurchasesByCreditCardUseCase(mock_unit_of_work)

        result = use_case.execute(query)

        assert len(result) == 2
        assert result[0].purchase_date == date(2025, 1, 20)  # Most recent first
        assert result[1].purchase_date == date(2025, 1, 10)


class TestListPurchasesByDateRangeUseCase:

    def test_should_return_purchases_within_date_range(self, mock_unit_of_work):
        """
        GIVEN: Purchases in different dates
        WHEN: Execute query with date range
        THEN: Returns only purchases within range
        """
        all_purchases = [
            Purchase(
                id=1,
                user_id=10,
                credit_card_id=1,
                category_id=1,
                purchase_date=date(2025, 1, 5),
                description="Before",
                total_amount=Money(Decimal("1000.00"), Currency.ARS),
                installments_count=1,
            ),
            Purchase(
                id=2,
                user_id=10,
                credit_card_id=1,
                category_id=1,
                purchase_date=date(2025, 1, 15),
                description="Within",
                total_amount=Money(Decimal("2000.00"), Currency.ARS),
                installments_count=1,
            ),
            Purchase(
                id=3,
                user_id=10,
                credit_card_id=1,
                category_id=1,
                purchase_date=date(2025, 1, 25),
                description="After",
                total_amount=Money(Decimal("3000.00"), Currency.ARS),
                installments_count=1,
            ),
        ]

        mock_unit_of_work.purchases.find_by_user_id.return_value = all_purchases

        query = ListPurchasesByDateRangeQuery(
            user_id=10, start_date=date(2025, 1, 10), end_date=date(2025, 1, 20)
        )
        use_case = ListPurchasesByDateRangeUseCase(mock_unit_of_work)

        result = use_case.execute(query)

        assert len(result) == 1
        assert result[0].id == 2

    def test_should_raise_error_when_start_after_end(self, mock_unit_of_work):
        """
        GIVEN: Invalid date range (start > end)
        WHEN: Execute query
        THEN: Raises ValueError
        """
        query = ListPurchasesByDateRangeQuery(
            user_id=10, start_date=date(2025, 1, 20), end_date=date(2025, 1, 10)
        )
        use_case = ListPurchasesByDateRangeUseCase(mock_unit_of_work)

        with pytest.raises(
            ValueError, match="start_date must be before or equal to end_date"
        ):
            use_case.execute(query)


class TestListCreditCardsByUserUseCase:

    def test_should_return_all_cards_for_user(self, mock_unit_of_work):
        """
        GIVEN: User with multiple credit cards
        WHEN: Execute query
        THEN: Returns all cards
        """
        cards = [
            CreditCard(
                id=1,
                user_id=10,
                name="Visa",
                bank="HSBC",
                last_four_digits="1234",
                billing_close_day=10,
                payment_due_day=20,
                credit_limit=None,
            ),
            CreditCard(
                id=2,
                user_id=10,
                name="MasterCard",
                bank="Santander",
                last_four_digits="5678",
                billing_close_day=15,
                payment_due_day=25,
                credit_limit=None,
            ),
        ]

        mock_unit_of_work.credit_cards.find_by_user_id.return_value = cards

        query = ListCreditCardsByUserQuery(user_id=10)
        use_case = ListCreditCardsByUserUseCase(mock_unit_of_work)

        result = use_case.execute(query)

        assert len(result) == 2
        assert result[0].name == "Visa"
        assert result[1].name == "MasterCard"
