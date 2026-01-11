"""
API integration tests for purchases endpoints.

Tests all purchase-related API endpoints with real database and FastAPI test client.
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
        "credit_limit_amount": 10000.00,
        "credit_limit_currency": "ARS",
    }
    response = client.post(
        "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


class TestCreatePurchase:
    """Test POST /api/v1/purchases"""

    def test_should_create_purchase_with_installments(
        self, client, test_user, test_credit_card, test_category
    ):
        """Should create purchase and generate installments"""
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2025-01-15",
            "description": "Test Purchase",
            "total_amount": 3000.00,
            "total_currency": "ARS",
            "installments_count": 3,
        }

        response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Test Purchase"
        assert data["total_amount"] == "3000.00"
        assert data["installments_count"] == 3
        assert data["payment_method_id"] == test_credit_card["payment_method_id"]
        assert data["category_id"] == test_category["id"]

    def test_should_return_400_for_invalid_data(self, client, test_user):
        """Should return 400 for invalid purchase data"""
        invalid_data = {
            "payment_method_id": 999,  # Non-existent payment method
            "category_id": 999,  # Non-existent category
            "purchase_date": "2025-01-15",
            "description": "Test",
            "total_amount": 1000.00,
            "currency": "ARS",
            "installments_count": 3,
        }

        response = client.post(
            "/api/v1/purchases", json=invalid_data, params={"user_id": test_user["id"]}
        )

        assert response.status_code in [400, 404]


class TestGetPurchaseById:
    """Test GET /api/v1/purchases/{purchase_id}"""

    def test_should_return_purchase_by_id(
        self, client, test_user, test_credit_card, test_category
    ):
        """Should retrieve purchase by ID"""
        # Create purchase
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2025-01-15",
            "description": "Test Purchase",
            "total_amount": 1000.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }
        create_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
        )
        purchase_id = create_response.json()["id"]

        # Get purchase
        response = client.get(
            f"/api/v1/purchases/{purchase_id}", params={"user_id": test_user["id"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == purchase_id
        assert data["description"] == "Test Purchase"

    def test_should_return_404_for_nonexistent_purchase(self, client, test_user):
        """Should return 404 for non-existent purchase"""
        response = client.get(
            "/api/v1/purchases/999", params={"user_id": test_user["id"]}
        )

        assert response.status_code == 404


class TestListPurchases:
    """Test GET /api/v1/purchases"""

    def test_should_list_all_purchases_for_user(
        self, client, test_user, test_credit_card, test_category
    ):
        """Should list all purchases for user"""
        # Create multiple purchases
        for i in range(3):
            purchase_data = {
                "payment_method_id": test_credit_card["payment_method_id"],
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

        # List purchases
        response = client.get("/api/v1/purchases", params={"user_id": test_user["id"]})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Should be sorted by date (most recent first)
        assert data[0]["description"] == "Purchase 3"
        assert data[1]["description"] == "Purchase 2"
        assert data[2]["description"] == "Purchase 1"

    def test_should_filter_by_date_range(
        self, client, test_user, test_credit_card, test_category
    ):
        """Should filter purchases by date range"""
        # Create purchases on different dates
        dates = ["2025-01-10", "2025-01-15", "2025-01-20"]
        for i, purchase_date in enumerate(dates):
            purchase_data = {
                "payment_method_id": test_credit_card["payment_method_id"],
                "category_id": test_category["id"],
                "purchase_date": purchase_date,
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

        # Filter by date range
        response = client.get(
            "/api/v1/purchases",
            params={
                "user_id": test_user["id"],
                "start_date": "2025-01-12",
                "end_date": "2025-01-18",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["description"] == "Purchase 2"

    def test_should_return_400_for_invalid_date_range(self, client, test_user):
        """Should return 400 when start_date > end_date"""
        response = client.get(
            "/api/v1/purchases",
            params={
                "user_id": test_user["id"],
                "start_date": "2025-01-20",
                "end_date": "2025-01-10",
            },
        )

        assert response.status_code == 400

    def test_should_support_pagination(
        self, client, test_user, test_credit_card, test_category
    ):
        """Should support pagination with skip and limit"""
        # Create 10 purchases
        for i in range(10):
            purchase_data = {
                "payment_method_id": test_credit_card["payment_method_id"],
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
            "/api/v1/purchases",
            params={"user_id": test_user["id"], "skip": 2, "limit": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


class TestListInstallmentsByPurchase:
    """Test GET /api/v1/purchases/{purchase_id}/installments"""

    def test_should_list_installments_for_purchase(
        self, client, test_user, test_credit_card, test_category
    ):
        """Should list all installments for a purchase"""
        # Create purchase with 3 installments
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2025-01-15",
            "description": "Test Purchase",
            "total_amount": 3000.00,
            "total_currency": "ARS",
            "installments_count": 3,
        }
        create_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
        )
        purchase_id = create_response.json()["id"]

        # Get installments
        response = client.get(
            f"/api/v1/purchases/{purchase_id}/installments",
            params={"user_id": test_user["id"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Should be sorted by installment_number
        assert data[0]["installment_number"] == 1
        assert data[1]["installment_number"] == 2
        assert data[2]["installment_number"] == 3
        # First installment should have the remainder
        assert data[0]["amount"] == "1000.00"

    def test_should_return_404_for_nonexistent_purchase(self, client, test_user):
        """Should return 404 for non-existent purchase"""
        response = client.get(
            "/api/v1/purchases/999/installments", params={"user_id": test_user["id"]}
        )

        assert response.status_code == 404


class TestUpdatePurchase:
    """Test PATCH /api/v1/purchases/{purchase_id}"""

    def test_patch_purchase_description_returns_200(
        self, client, test_user, test_credit_card, test_category
    ):
        """Should update purchase description successfully"""
        # Create purchase
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2025-01-15",
            "description": "Original Description",
            "total_amount": 1000.00,
            "currency": "ARS",
            "installments_count": 1,
        }

        create_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
        )
        assert create_response.status_code == 201
        purchase = create_response.json()

        # Update description
        update_data = {"description": "Updated Description"}
        response = client.patch(
            f"/api/v1/purchases/{purchase['id']}",
            json=update_data,
            params={"user_id": test_user["id"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated Description"
        assert data["total_amount"] == "1000.00"  # Unchanged

    def test_patch_purchase_invalid_id_returns_404(self, client, test_user):
        """Should return 404 for invalid purchase ID"""
        update_data = {"description": "Updated Description"}
        response = client.patch(
            "/api/v1/purchases/999",
            json=update_data,
            params={"user_id": test_user["id"]}
        )

        assert response.status_code == 404

    def test_patch_purchase_wrong_user_returns_404(self, client, test_user, test_credit_card, test_category):
        """Should return 404 when user doesn't own the purchase"""
        # Create purchase for test_user
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2025-01-15",
            "description": "Test Purchase",
            "total_amount": 1000.00,
            "currency": "ARS",
            "installments_count": 1,
        }

        create_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
        )
        assert create_response.status_code == 201
        purchase = create_response.json()

        # Try to update with different user ID
        update_data = {"description": "Updated Description"}
        response = client.patch(
            f"/api/v1/purchases/{purchase['id']}",
            json=update_data,
            params={"user_id": 999}  # Wrong user
        )

        assert response.status_code == 404

    def test_patch_purchase_amount_single_installment_updates_both(
        self, client, test_user, test_credit_card, test_category
    ):
        """Should update both purchase total and single installment amount"""
        # Create single installment purchase
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2025-01-15",
            "description": "Test Purchase",
            "total_amount": 1000.00,
            "currency": "ARS",
            "installments_count": 1,
        }

        create_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
        )
        assert create_response.status_code == 201
        purchase = create_response.json()

        # Update amount
        update_data = {"total_amount": 1500.00}
        response = client.patch(
            f"/api/v1/purchases/{purchase['id']}",
            json=update_data,
            params={"user_id": test_user["id"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_amount"] == "1500.00"

        # Verify installment was also updated
        installments_response = client.get(
            f"/api/v1/purchases/{purchase['id']}/installments",
            params={"user_id": test_user["id"]}
        )
        assert installments_response.status_code == 200
        installments = installments_response.json()
        assert len(installments) == 1
        assert installments[0]["amount"] == "1500.00"

    def test_patch_purchase_amount_multiple_installments_returns_400(
        self, client, test_user, test_credit_card, test_category
    ):
        """Should return 400 when trying to update amount for multi-installment purchase"""
        # Create multi-installment purchase
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2025-01-15",
            "description": "Test Purchase",
            "total_amount": 3000.00,
            "currency": "ARS",
            "installments_count": 3,
        }

        create_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
        )
        assert create_response.status_code == 201
        purchase = create_response.json()

        # Try to update amount (should fail)
        update_data = {"total_amount": 4000.00}
        response = client.patch(
            f"/api/v1/purchases/{purchase['id']}",
            json=update_data,
            params={"user_id": test_user["id"]}
        )

        assert response.status_code == 400
