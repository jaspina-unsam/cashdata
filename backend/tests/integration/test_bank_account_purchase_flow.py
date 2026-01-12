"""
End-to-end flow tests for bank account purchases.

Tests complete workflows for creating and managing bank account purchases
including dual ownership scenarios.
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


class TestBankAccountPurchaseFlow:
    """Test complete bank account purchase workflow including dual ownership"""

    def test_create_account_with_single_owner(self, client, db_session):
        """
        Test creating a bank account with a single owner (primary user only).
        """
        # Create user
        user = create_user_in_db(db_session, "Alice Brown", "alice@example.com")
        user_id = user["id"]

        # Create bank account with single owner
        bank_account_data = {
            "primary_user_id": user_id,
            "secondary_user_id": None,
            "name": "Alice's Savings",
            "bank": "Banco Nación",
            "account_type": "Caja de Ahorro",
            "last_four_digits": "5678",
            "currency": "ARS",
        }
        bank_response = client.post("/api/v1/bank-accounts", json=bank_account_data)
        assert bank_response.status_code == 201
        bank_account = bank_response.json()

        # Verify bank account was created correctly
        assert bank_account["primary_user_id"] == user_id
        assert bank_account["secondary_user_id"] is None
        assert bank_account["name"] == "Alice's Savings"
        assert bank_account["bank"] == "Banco Nación"
        assert bank_account["account_type"] == "Caja de Ahorro"
        assert bank_account["last_four_digits"] == "5678"
        assert bank_account["currency"] == "ARS"
        assert "payment_method_id" in bank_account

    def test_create_account_with_two_owners(self, client, db_session):
        """
        Test creating a bank account with two owners (primary and secondary users).
        """
        # Create two users
        user1 = create_user_in_db(db_session, "Bob Smith", "bob@example.com")
        user2 = create_user_in_db(db_session, "Carol White", "carol@example.com")
        user1_id = user1["id"]
        user2_id = user2["id"]

        # Create bank account with two owners
        bank_account_data = {
            "primary_user_id": user1_id,
            "secondary_user_id": user2_id,
            "name": "Joint Account",
            "bank": "Banco Santander",
            "account_type": "Cuenta Corriente",
            "last_four_digits": "9012",
            "currency": "ARS",
        }
        bank_response = client.post("/api/v1/bank-accounts", json=bank_account_data)
        assert bank_response.status_code == 201
        bank_account = bank_response.json()

        # Verify bank account was created correctly
        assert bank_account["primary_user_id"] == user1_id
        assert bank_account["secondary_user_id"] == user2_id
        assert bank_account["name"] == "Joint Account"
        assert "payment_method_id" in bank_account
        payment_method_id = bank_account["payment_method_id"]

        # Verify both users can see the bank account
        user1_accounts = client.get(
            "/api/v1/bank-accounts", params={"user_id": user1_id}
        )
        assert user1_accounts.status_code == 200
        assert len(user1_accounts.json()) >= 1
        assert any(acc["id"] == bank_account["id"] for acc in user1_accounts.json())

        user2_accounts = client.get(
            "/api/v1/bank-accounts", params={"user_id": user2_id}
        )
        assert user2_accounts.status_code == 200
        assert len(user2_accounts.json()) >= 1
        assert any(acc["id"] == bank_account["id"] for acc in user2_accounts.json())

    def test_primary_user_can_create_purchase(self, client, db_session):
        """
        Test that the primary user can create a purchase using the bank account.
        """
        # Create two users
        user1 = create_user_in_db(db_session, "David Lee", "david@example.com")
        user2 = create_user_in_db(db_session, "Emma Wilson", "emma@example.com")
        user1_id = user1["id"]
        user2_id = user2["id"]

        # Create category
        category_data = {"name": "Groceries", "color": "#4CAF50"}
        category_response = client.post("/api/v1/categories", json=category_data)
        assert category_response.status_code == 201
        category_id = category_response.json()["id"]

        # Create joint bank account
        bank_account_data = {
            "primary_user_id": user1_id,
            "secondary_user_id": user2_id,
            "name": "Shared Account",
            "bank": "Banco Galicia",
            "account_type": "Caja de Ahorro",
            "last_four_digits": "3456",
            "currency": "ARS",
        }
        bank_response = client.post("/api/v1/bank-accounts", json=bank_account_data)
        assert bank_response.status_code == 201
        payment_method_id = bank_response.json()["payment_method_id"]

        # Primary user creates a purchase
        purchase_data = {
            "payment_method_id": payment_method_id,
            "category_id": category_id,
            "purchase_date": "2025-01-15",
            "description": "Supermercado (David)",
            "total_amount": 25000.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }
        purchase_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": user1_id}
        )
        assert purchase_response.status_code == 201
        purchase = purchase_response.json()

        # Verify purchase details
        assert purchase["description"] == "Supermercado (David)"
        assert purchase["total_amount"] == "25000.00"
        assert purchase["installments_count"] == 1
        assert purchase["user_id"] == user1_id
        assert purchase["payment_method_id"] == payment_method_id

        # Verify no installments are created for bank account purchases
        installments_response = client.get(
            f"/api/v1/purchases/{purchase['id']}/installments",
            params={"user_id": user1_id},
        )
        assert installments_response.status_code == 200
        assert len(installments_response.json()) == 0

    def test_secondary_user_can_create_purchase(self, client, db_session):
        """
        Test that the secondary user can also create a purchase using the bank account.
        """
        # Create two users
        user1 = create_user_in_db(db_session, "Frank Miller", "frank@example.com")
        user2 = create_user_in_db(db_session, "Grace Taylor", "grace@example.com")
        user1_id = user1["id"]
        user2_id = user2["id"]

        # Create category
        category_data = {"name": "Utilities", "color": "#FF5722"}
        category_response = client.post("/api/v1/categories", json=category_data)
        assert category_response.status_code == 201
        category_id = category_response.json()["id"]

        # Create joint bank account
        bank_account_data = {
            "primary_user_id": user1_id,
            "secondary_user_id": user2_id,
            "name": "Household Account",
            "bank": "Banco BBVA",
            "account_type": "Cuenta Corriente",
            "last_four_digits": "7890",
            "currency": "ARS",
        }
        bank_response = client.post("/api/v1/bank-accounts", json=bank_account_data)
        assert bank_response.status_code == 201
        payment_method_id = bank_response.json()["payment_method_id"]

        # Secondary user creates a purchase
        purchase_data = {
            "payment_method_id": payment_method_id,
            "category_id": category_id,
            "purchase_date": "2025-01-16",
            "description": "Pago de servicios (Grace)",
            "total_amount": 15000.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }
        purchase_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": user2_id}
        )
        assert purchase_response.status_code == 201
        purchase = purchase_response.json()

        # Verify purchase details
        assert purchase["description"] == "Pago de servicios (Grace)"
        assert purchase["total_amount"] == "15000.00"
        assert purchase["user_id"] == user2_id
        assert purchase["payment_method_id"] == payment_method_id

    def test_unauthorized_user_cannot_create_purchase(self, client, db_session):
        """
        Test that a user without access to the bank account cannot create a purchase.
        """
        # Create three users
        user1 = create_user_in_db(db_session, "Henry Davis", "henry@example.com")
        user2 = create_user_in_db(db_session, "Ivy Johnson", "ivy@example.com")
        user3 = create_user_in_db(
            db_session, "Jack Anderson", "jack@example.com"
        )  # Unauthorized user
        user1_id = user1["id"]
        user2_id = user2["id"]
        user3_id = user3["id"]

        # Create category
        category_data = {"name": "Entertainment", "color": "#9C27B0"}
        category_response = client.post("/api/v1/categories", json=category_data)
        assert category_response.status_code == 201
        category_id = category_response.json()["id"]

        # Create joint bank account (user1 and user2 only)
        bank_account_data = {
            "primary_user_id": user1_id,
            "secondary_user_id": user2_id,
            "name": "Private Account",
            "bank": "Banco Macro",
            "account_type": "Caja de Ahorro",
            "last_four_digits": "1122",
            "currency": "ARS",
        }
        bank_response = client.post("/api/v1/bank-accounts", json=bank_account_data)
        assert bank_response.status_code == 201
        payment_method_id = bank_response.json()["payment_method_id"]

        # Unauthorized user (user3) tries to create a purchase
        purchase_data = {
            "payment_method_id": payment_method_id,
            "category_id": category_id,
            "purchase_date": "2025-01-17",
            "description": "Unauthorized purchase attempt",
            "total_amount": 10000.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }
        purchase_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": user3_id}
        )

        # Should fail with 400 Bad Request (ownership error)
        assert purchase_response.status_code == 400
        error_detail = purchase_response.json()["detail"]
        assert "access" in error_detail.lower() or "does not belong" in error_detail.lower()

    def test_bank_account_cannot_have_multiple_installments(self, client, db_session):
        """
        Test that bank account purchases cannot have multiple installments.
        Only credit cards can have installments > 1.
        """
        # Create user
        user = create_user_in_db(db_session, "Karen Martinez", "karen@example.com")
        user_id = user["id"]

        # Create category
        category_data = {"name": "Shopping", "color": "#FF9800"}
        category_response = client.post("/api/v1/categories", json=category_data)
        assert category_response.status_code == 201
        category_id = category_response.json()["id"]

        # Create bank account
        bank_account_data = {
            "primary_user_id": user_id,
            "secondary_user_id": None,
            "name": "Karen's Account",
            "bank": "Banco Patagonia",
            "account_type": "Caja de Ahorro",
            "last_four_digits": "4455",
            "currency": "ARS",
        }
        bank_response = client.post("/api/v1/bank-accounts", json=bank_account_data)
        assert bank_response.status_code == 201
        payment_method_id = bank_response.json()["payment_method_id"]

        # Try to create purchase with multiple installments (should fail)
        purchase_data = {
            "payment_method_id": payment_method_id,
            "category_id": category_id,
            "purchase_date": "2025-01-18",
            "description": "Invalid installment purchase",
            "total_amount": 30000.00,
            "total_currency": "ARS",
            "installments_count": 6,  # Should be rejected
        }
        purchase_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": user_id}
        )

        # Should return 400 Bad Request
        assert purchase_response.status_code == 400
        error_detail = purchase_response.json()["detail"]
        assert "installments" in error_detail.lower() or "credit card" in error_detail.lower()

    def test_multiple_purchases_on_same_bank_account(self, client, db_session):
        """
        Test creating multiple purchases on the same bank account by different owners.
        """
        # Create two users
        user1 = create_user_in_db(db_session, "Laura Garcia", "laura@example.com")
        user2 = create_user_in_db(db_session, "Mike Rodriguez", "mike@example.com")
        user1_id = user1["id"]
        user2_id = user2["id"]

        # Create categories
        category1_data = {"name": "Food", "color": "#8BC34A"}
        category1_response = client.post("/api/v1/categories", json=category1_data)
        assert category1_response.status_code == 201
        category1_id = category1_response.json()["id"]

        category2_data = {"name": "Transport", "color": "#2196F3"}
        category2_response = client.post("/api/v1/categories", json=category2_data)
        assert category2_response.status_code == 201
        category2_id = category2_response.json()["id"]

        # Create joint bank account
        bank_account_data = {
            "primary_user_id": user1_id,
            "secondary_user_id": user2_id,
            "name": "Family Account",
            "bank": "Banco Supervielle",
            "account_type": "Caja de Ahorro",
            "last_four_digits": "6677",
            "currency": "ARS",
        }
        bank_response = client.post("/api/v1/bank-accounts", json=bank_account_data)
        assert bank_response.status_code == 201
        payment_method_id = bank_response.json()["payment_method_id"]

        # User1 creates first purchase
        purchase1_data = {
            "payment_method_id": payment_method_id,
            "category_id": category1_id,
            "purchase_date": "2025-01-19",
            "description": "Restaurant (Laura)",
            "total_amount": 8000.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }
        purchase1_response = client.post(
            "/api/v1/purchases", json=purchase1_data, params={"user_id": user1_id}
        )
        assert purchase1_response.status_code == 201
        purchase1_id = purchase1_response.json()["id"]

        # User2 creates second purchase
        purchase2_data = {
            "payment_method_id": payment_method_id,
            "category_id": category2_id,
            "purchase_date": "2025-01-20",
            "description": "Uber (Mike)",
            "total_amount": 3500.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }
        purchase2_response = client.post(
            "/api/v1/purchases", json=purchase2_data, params={"user_id": user2_id}
        )
        assert purchase2_response.status_code == 201
        purchase2_id = purchase2_response.json()["id"]

        # Verify both purchases exist and are associated with different users
        purchases1 = client.get("/api/v1/purchases", params={"user_id": user1_id})
        assert purchases1.status_code == 200
        purchase1_ids = [p["id"] for p in purchases1.json()]
        assert purchase1_id in purchase1_ids

        purchases2 = client.get("/api/v1/purchases", params={"user_id": user2_id})
        assert purchases2.status_code == 200
        purchase2_ids = [p["id"] for p in purchases2.json()]
        assert purchase2_id in purchase2_ids

        # Verify both purchases use the same payment_method_id
        all_purchases = purchases1.json() + purchases2.json()
        bank_purchases = [
            p for p in all_purchases if p["payment_method_id"] == payment_method_id
        ]
        assert len(bank_purchases) >= 2

    def test_cannot_create_account_with_same_primary_and_secondary(
        self, client, db_session
    ):
        """
        Test that creating a bank account with same primary and secondary user fails.
        """
        # Create user
        user = create_user_in_db(db_session, "Nancy Thompson", "nancy@example.com")
        user_id = user["id"]

        # Try to create bank account with same user as primary and secondary
        bank_account_data = {
            "primary_user_id": user_id,
            "secondary_user_id": user_id,  # Same as primary - should fail
            "name": "Invalid Account",
            "bank": "Banco Test",
            "account_type": "Caja de Ahorro",
            "last_four_digits": "9999",
            "currency": "ARS",
        }
        bank_response = client.post("/api/v1/bank-accounts", json=bank_account_data)

        # Should return 400 Bad Request
        assert bank_response.status_code == 400
        error_detail = bank_response.json()["detail"]
        assert "same" in error_detail.lower()
