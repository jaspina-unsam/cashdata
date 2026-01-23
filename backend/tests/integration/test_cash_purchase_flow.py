"""
End-to-end flow tests for cash account purchases.

Tests complete workflows for creating and managing cash purchases.
"""

import pytest
from datetime import date

from app.domain.entities.user import User
from app.domain.value_objects.money import Money, Currency
from app.infrastructure.persistence.mappers.user_mapper import UserMapper


def create_user_in_db(db_session, name, email):
    """Helper function to create a user directly in the database"""
    user = User(id=None, name=name, email=email, wage=Money(50000, Currency.ARS))
    user_model = UserMapper.to_model(user)
    db_session.add(user_model)
    db_session.commit()
    db_session.refresh(user_model)
    return {"id": user_model.id, "name": user_model.name, "email": user_model.email}


class TestCashPurchaseFlow:
    """Test complete cash purchase workflow"""

    def test_complete_cash_purchase_flow(self, client, db_session):
        """
        Complete flow for cash purchases:
        1. Create user
        2. Create category
        3. Create cash account
        4. Create purchase with cash payment method
        5. Verify no installments are created
        6. Query purchases by payment method (cash account)
        """
        # 1. Create user
        user = create_user_in_db(db_session, "Jane Doe", "jane@example.com")
        user_id = user["id"]

        # 2. Create category
        category_data = {"name": "Groceries", "color": "#4CAF50"}
        category_response = client.post("/api/v1/categories", json=category_data)
        assert category_response.status_code == 201
        category = category_response.json()
        category_id = category["id"]

        # 3. Create cash account
        cash_account_data = {
            "user_id": user_id,
            "name": "Efectivo - Jane",
            "currency": "ARS",
        }
        cash_response = client.post("/api/v1/cash-accounts", json=cash_account_data)
        assert cash_response.status_code == 201
        cash_account = cash_response.json()
        
        # Verify cash account was created correctly
        assert cash_account["user_id"] == user_id
        assert cash_account["name"] == "Efectivo - Jane"
        assert cash_account["currency"] == "ARS"
        assert "payment_method_id" in cash_account
        payment_method_id = cash_account["payment_method_id"]

        # 4. Create purchase with cash payment method
        purchase_data = {
            "payment_method_id": payment_method_id,
            "category_id": category_id,
            "purchase_date": "2025-01-10",
            "description": "Compras del supermercado",
            "total_amount": 15000.00,
            "total_currency": "ARS",
            "installments_count": 1,  # Cash purchases must have installments_count = 1
        }
        purchase_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": user_id}
        )
        assert purchase_response.status_code == 201
        purchase = purchase_response.json()
        purchase_id = purchase["id"]

        # Verify purchase details
        assert purchase["description"] == "Compras del supermercado"
        assert purchase["total_amount"] == "15000.00"
        assert purchase["installments_count"] == 1
        assert purchase["payment_method_id"] == payment_method_id

        # 5. Verify no installments are created for cash purchases
        installments_response = client.get(
            f"/api/v1/purchases/{purchase_id}/installments", params={"user_id": user_id}
        )
        assert installments_response.status_code == 200
        installments = installments_response.json()
        
        # Cash purchases should not generate installments
        assert len(installments) == 0, "Cash purchases should not have installments"

        # 6. Query purchases by payment method (cash account)
        # Get all purchases for this user
        user_purchases_response = client.get(
            "/api/v1/purchases", params={"user_id": user_id}
        )
        assert user_purchases_response.status_code == 200
        data = user_purchases_response.json()
        
        # Should have at least our cash purchase
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        
        # Find our purchase in the list
        cash_purchase = next(
            (p for p in data["items"] if p["id"] == purchase_id), None
        )
        assert cash_purchase is not None, "Cash purchase should be in user's purchase list"
        assert cash_purchase["payment_method_id"] == payment_method_id

    def test_cash_purchase_cannot_have_multiple_installments(self, client, db_session):
        """
        Test that cash purchases cannot have multiple installments.
        Only credit card purchases can have installments_count > 1.
        """
        # Create user
        user = create_user_in_db(db_session, "John Smith", "john.smith@example.com")
        user_id = user["id"]

        # Create category
        category_data = {"name": "Shopping", "color": "#FF5722"}
        category_response = client.post("/api/v1/categories", json=category_data)
        assert category_response.status_code == 201
        category = category_response.json()
        category_id = category["id"]

        # Create cash account
        cash_account_data = {
            "user_id": user_id,
            "name": "Efectivo - John",
            "currency": "ARS",
        }
        cash_response = client.post("/api/v1/cash-accounts", json=cash_account_data)
        assert cash_response.status_code == 201
        cash_account = cash_response.json()
        payment_method_id = cash_account["payment_method_id"]

        # Try to create purchase with multiple installments (should fail)
        purchase_data = {
            "payment_method_id": payment_method_id,
            "category_id": category_id,
            "purchase_date": "2025-01-10",
            "description": "Invalid purchase",
            "total_amount": 10000.00,
            "total_currency": "ARS",
            "installments_count": 3,  # Should be rejected for cash
        }
        purchase_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": user_id}
        )
        
        # Should return 400 Bad Request
        assert purchase_response.status_code == 400
        error_detail = purchase_response.json()["detail"]
        assert "installments" in error_detail.lower() or "credit card" in error_detail.lower()

    def test_multiple_cash_purchases_same_account(self, client, db_session):
        """
        Test creating multiple cash purchases on the same cash account.
        """
        # Create user
        user = create_user_in_db(db_session, "Maria Lopez", "maria@example.com")
        user_id = user["id"]

        # Create categories
        category1_data = {"name": "Food", "color": "#FFC107"}
        category1_response = client.post("/api/v1/categories", json=category1_data)
        assert category1_response.status_code == 201
        category1_id = category1_response.json()["id"]

        category2_data = {"name": "Transport", "color": "#2196F3"}
        category2_response = client.post("/api/v1/categories", json=category2_data)
        assert category2_response.status_code == 201
        category2_id = category2_response.json()["id"]

        # Create cash account
        cash_account_data = {
            "user_id": user_id,
            "name": "Efectivo - Maria",
            "currency": "ARS",
        }
        cash_response = client.post("/api/v1/cash-accounts", json=cash_account_data)
        assert cash_response.status_code == 201
        payment_method_id = cash_response.json()["payment_method_id"]

        # Create first purchase
        purchase1_data = {
            "payment_method_id": payment_method_id,
            "category_id": category1_id,
            "purchase_date": "2025-01-10",
            "description": "Almuerzo",
            "total_amount": 5000.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }
        purchase1_response = client.post(
            "/api/v1/purchases", json=purchase1_data, params={"user_id": user_id}
        )
        assert purchase1_response.status_code == 201
        purchase1_id = purchase1_response.json()["id"]

        # Create second purchase
        purchase2_data = {
            "payment_method_id": payment_method_id,
            "category_id": category2_id,
            "purchase_date": "2025-01-11",
            "description": "Taxi",
            "total_amount": 2500.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }
        purchase2_response = client.post(
            "/api/v1/purchases", json=purchase2_data, params={"user_id": user_id}
        )
        assert purchase2_response.status_code == 201
        purchase2_id = purchase2_response.json()["id"]

        # Query all purchases for this user
        user_purchases_response = client.get(
            "/api/v1/purchases", params={"user_id": user_id}
        )
        assert user_purchases_response.status_code == 200
        data = user_purchases_response.json()
        
        # Both purchases should be in the list
        purchase_ids = [p["id"] for p in data["items"]]
        assert purchase1_id in purchase_ids
        assert purchase2_id in purchase_ids
        
        # Both should have the same payment_method_id
        cash_purchases = [
            p for p in data["items"] if p["payment_method_id"] == payment_method_id
        ]
        assert len(cash_purchases) >= 2, "Should have at least 2 purchases for this cash account"

    def test_cannot_create_duplicate_currency_cash_account(self, client, db_session):
        """
        Test that a user cannot create multiple cash accounts with the same currency.
        """
        # Create user
        user = create_user_in_db(db_session, "Pedro Garcia", "pedro@example.com")
        user_id = user["id"]

        # Create first cash account with ARS
        cash_account_data1 = {
            "user_id": user_id,
            "name": "Efectivo Principal",
            "currency": "ARS",
        }
        cash_response1 = client.post("/api/v1/cash-accounts", json=cash_account_data1)
        assert cash_response1.status_code == 201

        # Try to create second cash account with same currency (should fail)
        cash_account_data2 = {
            "user_id": user_id,
            "name": "Efectivo Secundario",
            "currency": "ARS",
        }
        cash_response2 = client.post("/api/v1/cash-accounts", json=cash_account_data2)
        
        # Should return 400 Bad Request
        assert cash_response2.status_code == 400
        error_detail = cash_response2.json()["detail"]
        assert "already exists" in error_detail.lower()

    def test_can_create_cash_accounts_different_currencies(self, client, db_session):
        """
        Test that a user CAN create multiple cash accounts with different currencies.
        """
        # Create user
        user = create_user_in_db(db_session, "Laura Martinez", "laura@example.com")
        user_id = user["id"]

        # Create ARS cash account
        cash_account_ars = {
            "user_id": user_id,
            "name": "Efectivo Pesos",
            "currency": "ARS",
        }
        ars_response = client.post("/api/v1/cash-accounts", json=cash_account_ars)
        assert ars_response.status_code == 201
        ars_account = ars_response.json()
        assert ars_account["currency"] == "ARS"

        # Create USD cash account (should succeed)
        cash_account_usd = {
            "user_id": user_id,
            "name": "Efectivo Dólares",
            "currency": "USD",
        }
        usd_response = client.post("/api/v1/cash-accounts", json=cash_account_usd)
        assert usd_response.status_code == 201
        usd_account = usd_response.json()
        assert usd_account["currency"] == "USD"

        # Get all cash accounts for this user
        user_cash_accounts = client.get(
            f"/api/v1/cash-accounts/user/{user_id}"
        )
        assert user_cash_accounts.status_code == 200
        accounts = user_cash_accounts.json()
        
        # Should have both accounts
        assert len(accounts) >= 2
        currencies = {acc["currency"] for acc in accounts}
        assert "ARS" in currencies
        assert "USD" in currencies
