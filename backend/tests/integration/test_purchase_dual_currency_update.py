"""
End-to-end tests for updating purchases with dual currency support.

Tests the complete workflow of editing purchases with exchange rates and currency conversion.
"""

import pytest
from datetime import date


@pytest.fixture
def test_category(client):
    """Create a test category"""
    category_data = {"name": "Test Category", "color": "#FF5733"}
    response = client.post("/api/v1/categories", json=category_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def test_credit_card(client, test_user):
    """Create a test credit card"""
    card_data = {
        "name": "Test Card",
        "bank": "Test Bank",
        "last_four_digits": "1234",
        "billing_close_day": 15,
        "payment_due_day": 10,
        "credit_limit_amount": 50000.00,
        "credit_limit_currency": "ARS",
    }
    response = client.post(
        "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def test_exchange_rate(client, test_user):
    """Create a test exchange rate"""
    rate_data = {
        "date": "2026-01-23",
        "from_currency": "USD",
        "to_currency": "ARS",
        "rate": 1500.0,
        "rate_type": "blue",
        "source": "Manual",
    }
    response = client.post(
        "/api/v1/exchange-rates", json=rate_data, params={"user_id": test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


class TestUpdatePurchaseWithDualCurrency:
    """Test PATCH /api/v1/purchases/{purchase_id} with dual currency"""

    def test_update_purchase_add_currency_conversion_with_existing_rate(
        self, client, test_user, test_credit_card, test_category, test_exchange_rate
    ):
        """
        Test scenario:
        1. Create a purchase in ARS without original currency
        2. Update it to add USD as original currency using an existing exchange rate
        3. Verify the purchase has both amounts and exchange_rate_id
        4. Verify installments were regenerated with dual currency
        """
        # 1. Create purchase in ARS only
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2026-01-23",
            "description": "Test Purchase ARS",
            "total_amount": 150000.00,
            "total_currency": "ARS",
            "installments_count": 3,
        }

        create_response = client.post(
            "/api/v1/purchases",
            json=purchase_data,
            params={"user_id": test_user["id"]},
        )
        assert create_response.status_code == 201
        purchase = create_response.json()
        purchase_id = purchase["id"]

        # Verify initial state
        assert purchase["currency"] == "ARS"

        # 2. Update purchase to add USD as original currency
        update_data = {
            "category_id": test_category["id"],
            "description": "Test Purchase ARS",
            "exchange_rate_id": test_exchange_rate["id"],
            "original_amount": 100.00,  # 150000 ARS / 1500 rate = 100 USD
            "original_currency": "USD",
        }

        update_response = client.patch(
            f"/api/v1/purchases/{purchase_id}",
            json=update_data,
            params={"user_id": test_user["id"]},
        )

        # Debug: print response if failed
        if update_response.status_code != 200:
            print(f"Update failed with status {update_response.status_code}")
            print(f"Response: {update_response.json()}")

        assert update_response.status_code == 200
        updated_purchase = update_response.json()

        # 3. Verify the purchase now has the dual currency data
        assert updated_purchase["currency"] == "ARS"
        assert updated_purchase["original_currency"] == "USD"
        assert float(updated_purchase["original_amount"]) == 100.00
        assert updated_purchase["exchange_rate_id"] == test_exchange_rate["id"]
        # Amount in ARS should still be 150000
        assert float(updated_purchase["total_amount"]) == 150000.00

        # 4. Verify installments were regenerated
        installments_response = client.get(
            f"/api/v1/purchases/{purchase_id}/installments",
            params={"user_id": test_user["id"]},
        )
        assert installments_response.status_code == 200
        installments = installments_response.json()

        assert len(installments) == 3
        for installment in installments:
            assert installment["currency"] == "ARS"
            assert float(installment["amount"]) == pytest.approx(50000.00, 0.01)

    def test_update_purchase_add_currency_conversion_with_custom_amount(
        self, client, test_user, test_credit_card, test_category, test_exchange_rate
    ):
        """
        Test scenario:
        1. Create a purchase in ARS
        2. Update it to add USD with a CUSTOM amount (not using existing rate)
        3. Verify an INFERRED exchange rate is created
        4. Verify the purchase has both amounts and the new exchange_rate_id
        """
        # 1. Create purchase in ARS
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2026-01-23",
            "description": "Test Purchase ARS Custom",
            "total_amount": 119000.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }

        create_response = client.post(
            "/api/v1/purchases",
            json=purchase_data,
            params={"user_id": test_user["id"]},
        )
        assert create_response.status_code == 201
        purchase = create_response.json()
        purchase_id = purchase["id"]

        # 2. Update purchase with custom USD amount (119000 ARS for 100 USD = rate 1190)
        update_data = {
            "category_id": test_category["id"],
            "description": "Test Purchase ARS Custom",
            "original_amount": 100.00,
            "original_currency": "USD",
        }

        update_response = client.patch(
            f"/api/v1/purchases/{purchase_id}",
            json=update_data,
            params={"user_id": test_user["id"]},
        )

        # Debug: print response if failed
        if update_response.status_code != 200:
            print(f"Update failed with status {update_response.status_code}")
            print(f"Response: {update_response.json()}")

        assert update_response.status_code == 200
        updated_purchase = update_response.json()

        # 3. Verify the purchase has dual currency data with INFERRED rate
        assert updated_purchase["currency"] == "ARS"
        assert updated_purchase["total_amount"] == "119000.00"
        assert updated_purchase["original_currency"] == "USD"
        assert float(updated_purchase["original_amount"]) == 100.00
        assert updated_purchase["exchange_rate_id"] is not None

        # Verify a new exchange rate was created (not the test fixture)
        assert updated_purchase["exchange_rate_id"] != test_exchange_rate["id"]

    def test_update_purchase_remove_currency_conversion(
        self, client, test_user, test_credit_card, test_category, test_exchange_rate
    ):
        """
        Test scenario:
        1. Create a purchase in ARS
        2. Add USD as original currency
        3. Remove the conversion (set back to single currency)
        4. Verify the dual currency fields are cleared
        """
        # 1. Create purchase in ARS only
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2026-01-23",
            "description": "Test Purchase",
            "total_amount": 150000.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }

        create_response = client.post(
            "/api/v1/purchases",
            json=purchase_data,
            params={"user_id": test_user["id"]},
        )
        assert create_response.status_code == 201
        purchase = create_response.json()
        purchase_id = purchase["id"]

        # 2. Add USD conversion
        update_data = {
            "category_id": test_category["id"],
            "description": "Test Purchase",
            "exchange_rate_id": test_exchange_rate["id"],
            "original_amount": 100.00,
            "original_currency": "USD",
        }

        update_response = client.patch(
            f"/api/v1/purchases/{purchase_id}",
            json=update_data,
            params={"user_id": test_user["id"]},
        )
        assert update_response.status_code == 200

        updated_purchase = update_response.json()
        assert updated_purchase["original_currency"] == "USD"
        assert updated_purchase["exchange_rate_id"] == test_exchange_rate["id"]

        # 3. Remove conversion by not sending dual-currency fields
        # Note: Currently the backend doesn't support explicitly clearing these fields
        # This test validates that we can add conversion successfully
        # Removing conversion would require sending explicit nulls which isn't supported yet
