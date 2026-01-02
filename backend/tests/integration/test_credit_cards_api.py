"""
API integration tests for credit cards endpoints.

Tests all credit card-related API endpoints with real database and FastAPI test client.
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


class TestCreateCreditCard:
    """Test POST /api/v1/credit-cards"""

    def test_should_create_credit_card(self, client, test_user):
        """Should create a credit card"""
        card_data = {
            "name": "Visa Gold",
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
        data = response.json()
        assert data["name"] == "Visa Gold"
        assert data["bank"] == "Test Bank"
        assert data["last_four_digits"] == "1234"
        assert data["billing_close_day"] == 15
        assert data["payment_due_day"] == 10
        assert data["credit_limit_amount"] == "50000.00"
        assert data["credit_limit_currency"] == "ARS"

    def test_should_create_card_without_credit_limit(self, client, test_user):
        """Should create card without credit limit"""
        card_data = {
            "name": "Basic Card",
            "bank": "Test Bank",
            "last_four_digits": "5678",
            "billing_close_day": 20,
            "payment_due_day": 15,
        }

        response = client.post(
            "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["credit_limit_amount"] is None
        assert data["credit_limit_currency"] is None


class TestListCreditCards:
    """Test GET /api/v1/credit-cards"""

    def test_should_list_all_cards_for_user(self, client, test_user):
        """Should list all credit cards for user"""
        # Create multiple cards
        card_names = ["Card 1", "Card 2", "Card 3"]
        for name in card_names:
            card_data = {
                "name": name,
                "bank": "Test Bank",
                "last_four_digits": "1234",
                "billing_close_day": 15,
                "payment_due_day": 10,
            }
            client.post(
                "/api/v1/credit-cards",
                json=card_data,
                params={"user_id": test_user["id"]},
            )

        # List cards
        response = client.get(
            "/api/v1/credit-cards", params={"user_id": test_user["id"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_should_support_pagination(self, client, test_user):
        """Should support pagination with skip and limit"""
        # Create 10 cards
        for i in range(10):
            card_data = {
                "name": f"Card {i+1}",
                "bank": "Test Bank",
                "last_four_digits": f"{i:04d}",
                "billing_close_day": 15,
                "payment_due_day": 10,
            }
            client.post(
                "/api/v1/credit-cards",
                json=card_data,
                params={"user_id": test_user["id"]},
            )

        # Test pagination
        response = client.get(
            "/api/v1/credit-cards",
            params={"user_id": test_user["id"], "skip": 3, "limit": 5},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5


class TestGetCreditCardById:
    """Test GET /api/v1/credit-cards/{card_id}"""

    def test_should_return_card_by_id(self, client, test_user):
        """Should retrieve credit card by ID"""
        # Create card
        card_data = {
            "name": "Test Card",
            "bank": "Test Bank",
            "last_four_digits": "1234",
            "billing_close_day": 15,
            "payment_due_day": 10,
        }
        create_response = client.post(
            "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
        )
        card_id = create_response.json()["id"]

        # Get card
        response = client.get(
            f"/api/v1/credit-cards/{card_id}", params={"user_id": test_user["id"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == card_id
        assert data["name"] == "Test Card"

    def test_should_return_404_for_nonexistent_card(self, client, test_user):
        """Should return 404 for non-existent card"""
        response = client.get(
            "/api/v1/credit-cards/999", params={"user_id": test_user["id"]}
        )

        assert response.status_code == 404


class TestGetCreditCardSummary:
    """Test GET /api/v1/credit-cards/{card_id}/summary"""

    def test_should_return_summary_for_billing_period(
        self, client, test_user, test_category
    ):
        """Should return credit card summary for billing period"""
        # Create card
        card_data = {
            "name": "Test Card",
            "bank": "Test Bank",
            "last_four_digits": "1234",
            "billing_close_day": 15,
            "payment_due_day": 10,
        }
        card_response = client.post(
            "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
        )
        card_id = card_response.json()["id"]

        # Create purchase with installments
        purchase_data = {
            "credit_card_id": card_id,
            "category_id": test_category["id"],
            "purchase_date": "2025-01-15",
            "description": "Test Purchase",
            "total_amount": 3000.00,
            "total_currency": "ARS",
            "installments_count": 3,
        }
        client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
        )

        # Get summary for February 2025 (should have 1 installment)
        response = client.get(
            f"/api/v1/credit-cards/{card_id}/summary",
            params={"user_id": test_user["id"], "billing_period": "202502"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["credit_card_id"] == card_id
        assert data["billing_period"] == "202502"
        assert len(data["installments"]) > 0

    def test_should_return_400_for_invalid_billing_period(self, client, test_user):
        """Should return 400 for invalid billing period format"""
        # Create card first
        card_data = {
            "name": "Test Card",
            "bank": "Test Bank",
            "last_four_digits": "1234",
            "billing_close_day": 15,
            "payment_due_day": 10,
        }
        card_response = client.post(
            "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
        )
        card_id = card_response.json()["id"]

        response = client.get(
            f"/api/v1/credit-cards/{card_id}/summary",
            params={
                "user_id": test_user["id"],
                "billing_period": "2025-01",  # Invalid format
            },
        )

        assert response.status_code == 422  # Validation error


class TestListPurchasesByCreditCard:
    """Test GET /api/v1/credit-cards/{card_id}/purchases"""

    def test_should_list_purchases_for_card(self, client, test_user, test_category):
        """Should list all purchases for a credit card"""
        # Create card
        card_data = {
            "name": "Test Card",
            "bank": "Test Bank",
            "last_four_digits": "1234",
            "billing_close_day": 15,
            "payment_due_day": 10,
        }
        card_response = client.post(
            "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
        )
        card_id = card_response.json()["id"]

        # Create multiple purchases
        for i in range(3):
            purchase_data = {
                "credit_card_id": card_id,
                "category_id": test_category["id"],
                "purchase_date": f"2025-01-{15+i}",
                "description": f"Purchase {i+1}",
                "total_amount": 1000.00 * (i + 1),
                "total_currency": "ARS",
                "installments_count": 1,
            }
            client.post(
                "/api/v1/purchases",
                json=purchase_data,
                params={"user_id": test_user["id"]},
            )

        # List purchases for card
        response = client.get(
            f"/api/v1/credit-cards/{card_id}/purchases",
            params={"user_id": test_user["id"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Should be sorted by date (most recent first)
        assert data[0]["description"] == "Purchase 3"
        assert data[1]["description"] == "Purchase 2"
        assert data[2]["description"] == "Purchase 1"

    def test_should_return_404_for_nonexistent_card(self, client, test_user):
        """Should return 404 for non-existent card"""
        response = client.get(
            "/api/v1/credit-cards/999/purchases", params={"user_id": test_user["id"]}
        )

        assert response.status_code == 404

    def test_should_support_pagination(self, client, test_user, test_category):
        """Should support pagination"""
        # Create card
        card_data = {
            "name": "Test Card",
            "bank": "Test Bank",
            "last_four_digits": "1234",
            "billing_close_day": 15,
            "payment_due_day": 10,
        }
        card_response = client.post(
            "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
        )
        card_id = card_response.json()["id"]

        # Create 10 purchases
        for i in range(10):
            purchase_data = {
                "credit_card_id": card_id,
                "category_id": test_category["id"],
                "purchase_date": f"2025-01-{10+i:02d}",
                "description": f"Purchase {i+1}",
                "total_amount": 1000.00,
                "total_currency": "ARS",
                "installments_count": 1,
            }
            client.post(
                "/api/v1/purchases",
                json=purchase_data,
                params={"user_id": test_user["id"]},
            )

        # Test pagination
        response = client.get(
            f"/api/v1/credit-cards/{card_id}/purchases",
            params={"user_id": test_user["id"], "skip": 2, "limit": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
