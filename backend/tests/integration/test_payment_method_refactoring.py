import pytest

# Note: Fixtures like client, test_user are provided by conftest.py


@pytest.fixture
def test_category(client, test_user):
    """Create a test category"""
    category_data = {
        "name": "Test Category",
        "color": "#FF0000",
        "icon": "shopping-cart",
    }
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
def test_cash_payment_method(client, test_user):
    """Create a test cash payment method"""
    # For now, create a payment method directly via credit card creation
    # Since we don't have a direct payment method creation API yet
    card_data = {
        "name": "Cash Method",
        "bank": "Cash Bank",
        "last_four_digits": "0000",
        "billing_close_day": 1,
        "payment_due_day": 1,
        "credit_limit_amount": None,
        "credit_limit_currency": None,
    }
    response = client.post(
        "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


class TestPaymentMethodRefactoring:
    """E2E tests for payment method refactoring"""

    def test_creating_credit_card_creates_payment_method(self, client, test_user):
        """Test: Crear credit card crea payment_method"""
        # Create credit card
        card_data = {
            "name": "Test Visa",
            "bank": "Test Bank",
            "last_four_digits": "5678",
            "billing_close_day": 20,
            "payment_due_day": 15,
            "credit_limit_amount": 50000.00,
            "credit_limit_currency": "ARS",
        }

        response = client.post(
            "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
        )
        assert response.status_code == 201
        credit_card = response.json()

        # Verify credit card has payment_method_id
        assert "payment_method_id" in credit_card
        assert credit_card["payment_method_id"] is not None

        # Verify payment method was created
        pm_response = client.get(
            f"/api/v1/payment-methods/{credit_card['payment_method_id']}",
            params={"user_id": test_user["id"]}
        )
        assert pm_response.status_code == 200
        payment_method = pm_response.json()

        assert payment_method["type"] == "credit_card"
        assert payment_method["name"] == "Test Visa"
        assert payment_method["user_id"] == test_user["id"]

    def test_creating_purchase_with_credit_card_works(self, client, test_user, test_credit_card, test_category):
        """Test: Crear purchase con credit_card funciona"""
        # Create purchase using credit card's payment method
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2025-01-15",
            "description": "Test Purchase",
            "total_amount": 5000.00,
            "currency": "ARS",
            "installments_count": 3,
        }

        response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
        )
        assert response.status_code == 201
        purchase = response.json()

        # Verify purchase was created with correct payment method
        assert purchase["payment_method_id"] == test_credit_card["payment_method_id"]
        assert purchase["installments_count"] == 3

        # Verify installments were created
        installments_response = client.get(
            f"/api/v1/purchases/{purchase['id']}/installments",
            params={"user_id": test_user["id"]}
        )
        assert installments_response.status_code == 200
        installments = installments_response.json()
        assert len(installments) == 3

    def test_can_create_purchase_with_installments_for_credit_card(self, client, test_user, test_cash_payment_method, test_category):
        """Test: Se puede crear purchase con installments para credit_card"""
        # Create purchase with multiple installments using credit card
        purchase_data = {
            "payment_method_id": test_cash_payment_method["id"],
            "category_id": test_category["id"],
            "purchase_date": "2025-01-15",
            "description": "Credit Card Purchase with Installments",
            "total_amount": 1000.00,
            "currency": "ARS",
            "installments_count": 2,  # Valid for credit card
        }

        response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
        )
        assert response.status_code == 201

    def test_queries_by_payment_method_id_work(self, client, test_user, test_credit_card, test_category):
        """Test: Queries por payment_method_id funcionan"""
        # Create purchase
        purchase_data = {
            "payment_method_id": test_credit_card["payment_method_id"],
            "category_id": test_category["id"],
            "purchase_date": "2025-01-15",
            "description": "Query Test Purchase",
            "total_amount": 3000.00,
            "currency": "ARS",
            "installments_count": 1,
        }

        create_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": test_user["id"]}
        )
        assert create_response.status_code == 201
        purchase = create_response.json()

        # Query purchases by payment method
        query_response = client.get(
            f"/api/v1/purchases/by-payment-method/{test_credit_card['payment_method_id']}",
            params={"user_id": test_user["id"]}
        )
        assert query_response.status_code == 200
        purchases = query_response.json()

        # Verify purchase is returned
        assert len(purchases) >= 1
        found_purchase = next((p for p in purchases if p["id"] == purchase["id"]), None)
        assert found_purchase is not None
        assert found_purchase["payment_method_id"] == test_credit_card["payment_method_id"]