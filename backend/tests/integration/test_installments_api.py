"""
API integration tests for installments endpoints.

Tests all installment-related API endpoints with real database and FastAPI test client.
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


@pytest.fixture
def test_purchase(client, test_user, test_credit_card, test_category):
    """Create a test purchase with installments"""
    purchase_data = {
        "payment_method_id": test_credit_card["id"],
        "category_id": test_category["id"],
        "purchase_date": "2025-01-15",
        "description": "Test Purchase",
        "total_amount": 3000.00,
        "currency": "ARS",
        "installments_count": 3,
    }

    response = client.post(
        "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def test_single_installment_purchase(client, test_user, test_credit_card, test_category):
    """Create a test purchase with single installment"""
    purchase_data = {
        "payment_method_id": test_credit_card["id"],
        "category_id": test_category["id"],
        "purchase_date": "2025-01-15",
        "description": "Single Installment Purchase",
        "total_amount": 1000.00,
        "currency": "ARS",
        "installments_count": 1,
    }

    response = client.post(
        "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


class TestUpdateInstallment:
    """Test PATCH /api/v1/installments/{installment_id}"""

    def test_patch_installment_amount_returns_200(
        self, client, test_user, test_purchase
    ):
        """Should update installment amount successfully"""
        # Get first installment
        installments_response = client.get(
            f"/api/v1/purchases/{test_purchase['id']}/installments",
            params={"user_id": test_user["id"]}
        )
        assert installments_response.status_code == 200
        installments = installments_response.json()
        first_installment = installments[0]

        # Update installment amount
        update_data = {"amount": 1500.00}
        response = client.patch(
            f"/api/v1/installments/{first_installment['id']}",
            json=update_data,
            params={"user_id": test_user["id"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == "1500.00"
        assert data["installment_number"] == 1

    def test_patch_installment_recalculates_purchase_total(
        self, client, test_user, test_purchase
    ):
        """Should recalculate purchase total when installment amount changes"""
        # Get installments
        installments_response = client.get(
            f"/api/v1/purchases/{test_purchase['id']}/installments",
            params={"user_id": test_user["id"]}
        )
        assert installments_response.status_code == 200
        installments = installments_response.json()

        # Update first installment amount
        first_installment = installments[0]
        update_data = {"amount": 1500.00}
        response = client.patch(
            f"/api/v1/installments/{first_installment['id']}",
            json=update_data,
            params={"user_id": test_user["id"]}
        )
        assert response.status_code == 200

        # Check that purchase total was recalculated
        purchase_response = client.get(
            f"/api/v1/purchases/{test_purchase['id']}",
            params={"user_id": test_user["id"]}
        )
        assert purchase_response.status_code == 200
        purchase = purchase_response.json()

        # Original: 3000 / 3 = 1000 each
        # After: 1500 + 1000 + 1000 = 3500
        assert purchase["total_amount"] == "3500.00"

    def test_patch_installment_invalid_id_returns_404(self, client, test_user):
        """Should return 404 for invalid installment ID"""
        update_data = {"amount": 1500.00}
        response = client.patch(
            "/api/v1/installments/999",
            json=update_data,
            params={"user_id": test_user["id"]}
        )

        assert response.status_code == 404

    def test_patch_installment_wrong_user_returns_403(
        self, client, test_user, test_purchase
    ):
        """Should return 403 when user doesn't own the installment"""
        # Get first installment
        installments_response = client.get(
            f"/api/v1/purchases/{test_purchase['id']}/installments",
            params={"user_id": test_user["id"]}
        )
        assert installments_response.status_code == 200
        installments = installments_response.json()
        first_installment = installments[0]

        # Try to update with different user ID
        update_data = {"amount": 1500.00}
        response = client.patch(
            f"/api/v1/installments/{first_installment['id']}",
            json=update_data,
            params={"user_id": 999}  # Wrong user
        )

        assert response.status_code == 403


class TestDeleteInstallment:
    """Test DELETE /api/v1/installments/{installment_id}"""

    def test_delete_installment_returns_204(
        self, client, test_user, test_purchase
    ):
        """Should delete installment successfully"""
        # Get installments
        installments_response = client.get(
            f"/api/v1/purchases/{test_purchase['id']}/installments",
            params={"user_id": test_user["id"]}
        )
        assert installments_response.status_code == 200
        installments = installments_response.json()
        assert len(installments) == 3

        # Delete first installment
        first_installment = installments[0]
        response = client.delete(
            f"/api/v1/installments/{first_installment['id']}",
            params={"user_id": test_user["id"]}
        )

        assert response.status_code == 204

        # Verify installment was deleted
        installments_response = client.get(
            f"/api/v1/purchases/{test_purchase['id']}/installments",
            params={"user_id": test_user["id"]}
        )
        assert installments_response.status_code == 200
        remaining_installments = installments_response.json()
        assert len(remaining_installments) == 2

        # Verify remaining installments keep their numbers
        assert remaining_installments[0]["installment_number"] == 2
        assert remaining_installments[1]["installment_number"] == 3

    def test_delete_last_installment_returns_422(
        self, client, test_user, test_single_installment_purchase
    ):
        """Should return 422 when trying to delete the last installment"""
        # Get the single installment
        installments_response = client.get(
            f"/api/v1/purchases/{test_single_installment_purchase['id']}/installments",
            params={"user_id": test_user["id"]}
        )
        assert installments_response.status_code == 200
        installments = installments_response.json()
        assert len(installments) == 1

        # Try to delete the last installment
        installment = installments[0]
        response = client.delete(
            f"/api/v1/installments/{installment['id']}",
            params={"user_id": test_user["id"]}
        )

        assert response.status_code == 422

    def test_delete_installment_wrong_user_returns_403(
        self, client, test_user, test_purchase
    ):
        """Should return 403 when user doesn't own the installment"""
        # Get first installment
        installments_response = client.get(
            f"/api/v1/purchases/{test_purchase['id']}/installments",
            params={"user_id": test_user["id"]}
        )
        assert installments_response.status_code == 200
        installments = installments_response.json()
        first_installment = installments[0]

        # Try to delete with different user ID
        response = client.delete(
            f"/api/v1/installments/{first_installment['id']}",
            params={"user_id": 999}  # Wrong user
        )

        assert response.status_code == 403