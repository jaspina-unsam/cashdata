"""E2E tests for monthly statement totals with dual-currency purchases."""

import pytest


class TestStatementDualCurrencyTotals:
    """Test statement total calculation with dual-currency purchases."""

    @pytest.fixture
    def test_credit_card(self, client, test_user):
        """Create a test ARS credit card"""
        card_data = {
            "name": "ARS Test Card",
            "bank": "Test Bank",
            "last_four_digits": "1234",
            "billing_close_day": 31,
            "payment_due_day": 10,
            "credit_limit_amount": 500000.00,
            "credit_limit_currency": "ARS",
        }
        response = client.post(
            "/api/v1/credit-cards",
            json=card_data,
            params={"user_id": test_user["id"]},
        )
        assert response.status_code == 201
        return response.json()

    @pytest.fixture
    def test_category(self, client, test_user):
        """Create a test category"""
        category_data = {"name": "Test Category", "color": "#FF5733"}
        response = client.post(
            "/api/v1/categories",
            json=category_data,
            params={"user_id": test_user["id"]},
        )
        assert response.status_code == 201
        return response.json()

    @pytest.fixture
    def exchange_rate(self, client, test_user):
        """Create a test exchange rate USD -> ARS via API."""
        rate_data = {
            "from_currency": "USD",
            "to_currency": "ARS",
            "rate": 1000.00,  # 1 USD = 1000 ARS
            "date": "2024-01-01",
            "rate_type": "blue",  # lowercase for StrEnum
            "source": "Test source",
        }
        response = client.post(
            "/api/v1/exchange-rates",
            json=rate_data,
            params={"user_id": test_user["id"]},
        )
        if response.status_code != 201:
            print(f"Failed to create exchange rate: {response.status_code}")
            print(f"Response: {response.json()}")
        assert response.status_code == 201
        return response.json()

    def test_statement_with_usd_purchases_should_convert_to_ars(
        self,
        client,
        test_user,
        test_credit_card,
        test_category,
        exchange_rate,
    ):
        """
        Given: An ARS credit card with a statement
        When: Creating USD purchases with exchange rates that fall in that statement
        Then: The statement total should be in ARS (not summing USD as ARS)
        
        Example:
        - Purchase 1: 100 USD x 1000 = 100,000 ARS (in 2 installments of 50 USD each)
        - Purchase 2: 50 USD x 1000 = 50,000 ARS (single payment)
        Expected total: 50,000 ARS (1st installment) + 50,000 ARS = 100,000 ARS
        NOT: 50 USD + 50 USD = 100 USD treated as 100 ARS
        """
        # Setup: Create statement for January 2024
        statement_data = {
            "credit_card_id": test_credit_card["id"],
            "start_date": "2024-01-01",
            "closing_date": "2024-01-31",
            "due_date": "2024-02-10",
        }
        
        create_statement_response = client.post(
            "/api/v1/statements",
            json=statement_data,
            params={"user_id": test_user["id"]},
        )
        assert create_statement_response.status_code == 201
        statement_id = create_statement_response.json()["id"]

        # Create first purchase: 100 USD in 2 installments = 100,000 ARS
        purchase1_data = {
            "description": "USD Purchase 1 - Two Installments",
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2024-01-15",
            "installments_count": 2,
            "total_amount": 100000.00,  # Converted amount in ARS (100 USD * 1000)
            "total_currency": "ARS",  # Card is in ARS
            "original_amount": 100.00,  # Paid in USD
            "original_currency": "USD",
            "exchange_rate_id": exchange_rate["id"],
        }
        
        purchase1_response = client.post(
            "/api/v1/purchases",
            json=purchase1_data,
            params={"user_id": test_user["id"]},
        )
        print(f"Purchase 1 response: {purchase1_response.status_code}")
        print(f"Purchase 1 data: {purchase1_response.json()}")
        assert purchase1_response.status_code == 201
        
        # Create second purchase: 50 USD in 1 installment = 50,000 ARS
        purchase2_data = {
            "description": "USD Purchase 2 - Single Payment",
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2024-01-20",
            "installments_count": 1,
            "total_amount": 50000.00,  # Converted amount in ARS (50 USD * 1000)
            "total_currency": "ARS",  # Card is in ARS
            "original_amount": 50.00,  # Paid in USD
            "original_currency": "USD",
            "exchange_rate_id": exchange_rate["id"],
        }
        
        purchase2_response = client.post(
            "/api/v1/purchases",
            json=purchase2_data,
            params={"user_id": test_user["id"]},
        )
        assert purchase2_response.status_code == 201

        # Get statement detail
        detail_response = client.get(
            f"/api/v1/statements/{statement_id}",
            params={"user_id": test_user["id"]},
        )
        assert detail_response.status_code == 200
        statement_detail = detail_response.json()
        
        print(f"\nStatement detail: {statement_detail}")
        print(f"Number of purchases: {len(statement_detail['purchases'])}")
        print(f"Total amount: {statement_detail['total_amount']} {statement_detail['currency']}")
        for i, p in enumerate(statement_detail['purchases']):
            print(f"Purchase {i}: {p['description']} - {p['amount']} {p['currency']}")
            print(f"  Original: {p.get('original_amount')} {p.get('original_currency')}")

        # Verify purchases are in the statement
        # Purchase 1 has 2 installments but only installment 1/2 is in January statement
        # Purchase 2 has 1 installment which is in January statement
        # Total: 2 installments should appear in January statement
        assert len(statement_detail["purchases"]) == 2  # installment 1/2 from purchase1 + installment 1/1 from purchase2

        # Calculate expected total in ARS
        # Purchase 1: 100 USD / 2 installments = 50 USD per installment
        # Purchase 2: 50 USD in 1 installment
        # Only installment 1/2 of purchase 1 appears in January (installment 2/2 would be in February)
        # So: (50 USD * 1000) + (50 USD * 1000) = 100,000 ARS
        # Purchase 1 has 100 USD total, 2 installments → each installment is 50 USD = 50,000 ARS
        # Purchase 2 has 50 USD total, 1 installment → 50 USD = 50,000 ARS
        # But only the FIRST installment of Purchase 1 falls in Jan 2024
        # So: 50,000 ARS (P1 installment 1) + 50,000 ARS (P2) = 100,000 ARS
        
        # Actually, the API might be calculating it wrong. Let's see what we get:
        actual_total = statement_detail["total_amount"]
        actual_currency = statement_detail["currency"]
        
        # The bug would be: summing 50 (USD) + 50 (USD) = 100 treated as ARS
        # The correct calculation: 50,000 ARS + 50,000 ARS = 100,000 ARS
        
        assert actual_currency == "ARS", f"Expected ARS but got {actual_currency}"
        
        # This should fail with current bug (expecting ~100 ARS instead of 100,000 ARS)
        expected_total = 100000.00  # 50k + 50k ARS
        assert actual_total == pytest.approx(expected_total, abs=1.0), (
            f"Statement total should be {expected_total} ARS, "
            f"but got {actual_total} ARS. "
            f"This suggests USD amounts are being summed as if they were ARS."
        )

    def test_statement_with_mixed_currency_purchases(
        self,
        client,
        test_user,
        test_credit_card,
        test_category,
        exchange_rate,
    ):
        """
        Test statement with both ARS and USD purchases.
        
        Given: An ARS card with statement
        When: Creating purchases in both ARS and USD
        Then: Total should correctly sum everything in ARS
        """
        # Create statement
        statement_data = {
            "credit_card_id": test_credit_card["id"],
            "start_date": "2024-01-01",
            "closing_date": "2024-01-31",
            "due_date": "2024-02-10",
        }
        
        create_response = client.post(
            "/api/v1/statements",
            json=statement_data,
            params={"user_id": test_user["id"]},
        )
        assert create_response.status_code == 201
        statement_id = create_response.json()["id"]

        # Create ARS purchase: 10,000 ARS
        ars_purchase = {
            "description": "ARS Purchase",
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2024-01-10",
            "installments_count": 1,
            "total_amount": 10000.00,
            "total_currency": "ARS",
        }
        
        client.post(
            "/api/v1/purchases",
            json=ars_purchase,
            params={"user_id": test_user["id"]},
        )

        # Create USD purchase: 20 USD = 20,000 ARS
        usd_purchase = {
            "description": "USD Purchase",
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2024-01-15",
            "installments_count": 1,
            "total_amount": 20000.00,  # Converted amount in ARS!
            "total_currency": "ARS",
            "original_amount": 20.00,
            "original_currency": "USD",
            "exchange_rate_id": exchange_rate["id"],
        }
        
        client.post(
            "/api/v1/purchases",
            json=usd_purchase,
            params={"user_id": test_user["id"]},
        )

        # Get statement
        response = client.get(
            f"/api/v1/statements/{statement_id}",
            params={"user_id": test_user["id"]},
        )
        assert response.status_code == 200
        data = response.json()

        # Expected: 10,000 ARS + 20,000 ARS = 30,000 ARS
        # Bug would give: 10,000 + 20 = 10,020 ARS
        assert data["currency"] == "ARS"
        assert data["total_amount"] == pytest.approx(30000.00, abs=1.0), (
            f"Expected 30,000 ARS but got {data['total_amount']} ARS"
        )

    def test_statement_shows_individual_purchases_in_correct_currency(
        self,
        client,
        test_user,
        test_credit_card,
        test_category,
        exchange_rate,
    ):
        """
        Test that individual purchases show correct amounts.
        
        Each purchase should show:
        - amount: in card currency (ARS)
        - currency: ARS
        - original_amount: in USD (if applicable)
        - original_currency: USD (if applicable)
        """
        # Create statement
        statement_data = {
            "credit_card_id": test_credit_card["id"],
            "start_date": "2024-01-01",
            "closing_date": "2024-01-31",
            "due_date": "2024-02-10",
        }
        
        create_response = client.post(
            "/api/v1/statements",
            json=statement_data,
            params={"user_id": test_user["id"]},
        )
        statement_id = create_response.json()["id"]

        # Create USD purchase: 100 USD = 100,000 ARS
        usd_purchase = {
            "description": "Test USD Purchase",
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2024-01-15",
            "installments_count": 1,
            "total_amount": 100000.00,  # Converted amount in ARS (100 USD * 1000)
            "total_currency": "ARS",
            "original_amount": 100.00,
            "original_currency": "USD",
            "exchange_rate_id": exchange_rate["id"],
        }
        
        client.post(
            "/api/v1/purchases",
            json=usd_purchase,
            params={"user_id": test_user["id"]},
        )

        # Get statement detail
        response = client.get(
            f"/api/v1/statements/{statement_id}",
            params={"user_id": test_user["id"]},
        )
        data = response.json()

        # Check individual purchase
        purchases = data["purchases"]
        assert len(purchases) == 1
        
        purchase = purchases[0]
        assert purchase["currency"] == "ARS", "Purchase amount should be in card currency (ARS)"
        assert purchase["amount"] == pytest.approx(100000.00, abs=1.0), (
            f"Purchase amount should be 100,000 ARS but got {purchase['amount']}"
        )
        assert purchase["original_currency"] == "USD"
        assert purchase["original_amount"] == pytest.approx(100.00, abs=0.01)
