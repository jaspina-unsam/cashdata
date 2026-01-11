"""
API integration tests for cash accounts endpoints.

Tests all cash account-related API endpoints with real database and FastAPI test client.
"""

import pytest


@pytest.fixture
def test_payment_method(client, test_user):
    """Create a test payment method"""
    pm_data = {
        "type": "cash",
        "name": "Test Cash PM",
    }
    response = client.post(
        "/api/v1/payment-methods", json=pm_data, params={"user_id": test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


class TestCreateCashAccount:
    """Test POST /api/v1/cash-accounts"""

    def test_should_create_cash_account(self, client, test_user):
        """Should create a cash account"""
        account_data = {
            "user_id": test_user["id"],
            "name": "Main Cash Account",
            "currency": "ARS",
        }

        response = client.post("/api/v1/cash-accounts", json=account_data)

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == test_user["id"]
        assert data["name"] == "Main Cash Account"
        assert data["currency"] == "ARS"

    def test_should_return_400_for_duplicate_currency(self, client, test_user):
        """Should return 400 when creating account with existing currency"""
        # Create first account
        account_data = {
            "user_id": test_user["id"],
            "name": "First Account",
            "currency": "ARS",
        }
        response1 = client.post("/api/v1/cash-accounts", json=account_data)
        assert response1.status_code == 201

        # Try to create second with same currency
        account_data2 = {
            "user_id": test_user["id"],
            "name": "Second Account",
            "currency": "ARS",
        }
        response2 = client.post("/api/v1/cash-accounts", json=account_data2)

        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]


class TestListCashAccounts:
    """Test GET /api/v1/cash-accounts"""

    def test_should_return_all_cash_accounts(self, client, test_user):
        """Should return all cash accounts"""
        # Create some accounts
        account_data1 = {
            "user_id": test_user["id"],
            "name": "Account 1",
            "currency": "ARS",
        }
        account_data2 = {
            "user_id": test_user["id"],
            "name": "Account 2",
            "currency": "USD",
        }
        client.post("/api/v1/cash-accounts", json=account_data1)
        client.post("/api/v1/cash-accounts", json=account_data2)

        response = client.get("/api/v1/cash-accounts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        names = [acc["name"] for acc in data]
        assert "Account 1" in names
        assert "Account 2" in names


class TestListCashAccountsByUserId:
    """Test GET /api/v1/cash-accounts/user/{user_id}"""

    def test_should_return_cash_accounts_for_user(self, client, test_user):
        """Should return cash accounts for specific user"""
        # Create accounts for the user
        account_data1 = {
            "user_id": test_user["id"],
            "name": "User Account 1",
            "currency": "ARS",
        }
        account_data2 = {
            "user_id": test_user["id"],
            "name": "User Account 2",
            "currency": "USD",
        }
        client.post("/api/v1/cash-accounts", json=account_data1)
        client.post("/api/v1/cash-accounts", json=account_data2)

        response = client.get(f"/api/v1/cash-accounts/user/{test_user['id']}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [acc["name"] for acc in data]
        assert "User Account 1" in names
        assert "User Account 2" in names

    def test_should_return_empty_list_for_user_without_accounts(self, client):
        """Should return empty list for user with no accounts"""
        response = client.get("/api/v1/cash-accounts/user/999")

        assert response.status_code == 200
        data = response.json()
        assert data == []


class TestDeleteCashAccount:
    """Test DELETE /api/v1/cash-accounts/{cash_account_id}"""

    def test_should_delete_cash_account(self, client, test_user):
        """Should delete a cash account"""
        # Create account
        account_data = {
            "user_id": test_user["id"],
            "name": "Account to Delete",
            "currency": "ARS",
        }
        create_response = client.post("/api/v1/cash-accounts", json=account_data)
        assert create_response.status_code == 201
        account_id = create_response.json()["id"]

        # Delete account
        delete_response = client.delete(f"/api/v1/cash-accounts/{account_id}")

        assert delete_response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api/v1/cash-accounts/user/{test_user['id']}")
        data = get_response.json()
        names = [acc["name"] for acc in data]
        assert "Account to Delete" not in names

    def test_should_return_404_for_nonexistent_account(self, client):
        """Should return 404 when deleting nonexistent account"""
        response = client.delete("/api/v1/cash-accounts/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]