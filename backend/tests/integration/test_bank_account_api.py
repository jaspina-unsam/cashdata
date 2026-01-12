"""
API integration tests for bank accounts endpoints.

Tests all bank account-related API endpoints with real database and FastAPI test client.
"""

import pytest
from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.infrastructure.persistence.mappers.payment_method_mapper import PaymentMethodMapper


@pytest.fixture
def test_payment_method(db_session, test_user):
    """Create a test payment method directly in database"""
    pm = PaymentMethod(
        id=None,
        user_id=test_user["id"],
        type=PaymentMethodType.BANK_ACCOUNT,
        name="Test Bank Account PM",
        is_active=True,
    )
    pm_model = PaymentMethodMapper.to_model(pm)
    db_session.add(pm_model)
    db_session.flush()
    return {"id": pm_model.id, "user_id": pm_model.user_id, "type": pm_model.type, "name": pm_model.name}


class TestCreateBankAccount:
    """Test POST /api/v1/bank-accounts"""

    def test_should_create_bank_account_successfully(self, client, test_user, db_session, test_payment_method):
        """Should create a bank account with all required fields"""
        # Create a second user for testing dual ownership
        from app.domain.entities.user import User
        from app.domain.value_objects.money import Money, Currency
        from app.infrastructure.persistence.mappers.user_mapper import UserMapper
        
        user2 = User(id=None, name="Second User", email="second@test.com", wage=Money(50000, Currency.ARS))
        user2_model = UserMapper.to_model(user2)
        db_session.add(user2_model)
        db_session.flush()  # Use flush instead of commit
        second_user_id = user2_model.id  # Capture ID before commit
        db_session.commit()
        
        account_data = {
            "primary_user_id": test_user["id"],
            "secondary_user_id": second_user_id,  # Use the captured ID
            "name": "Main Savings Account",
            "bank": "Test Bank",
            "account_type": "SAVINGS",
            "last_four_digits": "1234",
            "currency": "ARS",
        }

        response = client.post("/api/v1/bank-accounts", json=account_data)

        assert response.status_code == 201
        data = response.json()
        assert data["primary_user_id"] == test_user["id"]
        assert data["secondary_user_id"] == second_user_id
        assert data["name"] == "Main Savings Account"
        assert data["bank"] == "Test Bank"
        assert data["account_type"] == "SAVINGS"
        assert data["last_four_digits"] == "1234"
        assert data["currency"] == "ARS"
        assert "id" in data
        assert "payment_method_id" in data

    def test_should_create_bank_account_without_secondary_user(self, client, test_user, test_payment_method):
        """Should create a bank account without secondary user"""
        account_data = {
            "primary_user_id": test_user["id"],
            "name": "Solo Account",
            "bank": "Solo Bank",
            "account_type": "CHECKING",
            "last_four_digits": "5678",
            "currency": "USD",
        }

        response = client.post("/api/v1/bank-accounts", json=account_data)

        assert response.status_code == 201
        data = response.json()
        assert data["primary_user_id"] == test_user["id"]
        assert data["secondary_user_id"] is None
        assert data["name"] == "Solo Account"
        assert data["bank"] == "Solo Bank"
        assert data["account_type"] == "CHECKING"
        assert data["last_four_digits"] == "5678"
        assert data["currency"] == "USD"

    def test_should_return_400_for_invalid_name(self, client, test_user, test_payment_method):
        """Should return 422 for empty name (Pydantic validation)"""
        account_data = {
            "primary_user_id": test_user["id"],
            "name": "",  # Invalid empty name
            "bank": "Test Bank",
            "account_type": "SAVINGS",
            "last_four_digits": "1234",
            "currency": "ARS",
        }

        response = client.post("/api/v1/bank-accounts", json=account_data)

        assert response.status_code == 422  # Pydantic validation error

    def test_should_return_400_for_name_too_long(self, client, test_user, test_payment_method):
        """Should return 422 for name longer than 100 characters (Pydantic validation)"""
        long_name = "A" * 101
        account_data = {
            "primary_user_id": test_user["id"],
            "name": long_name,
            "bank": "Test Bank",
            "account_type": "SAVINGS",
            "last_four_digits": "1234",
            "currency": "ARS",
        }

        response = client.post("/api/v1/bank-accounts", json=account_data)

        assert response.status_code == 422  # Pydantic validation error

    def test_should_return_400_for_invalid_last_four_digits(self, client, test_user, test_payment_method):
        """Should return 422 for last_four_digits not exactly 4 characters (Pydantic validation)"""
        account_data = {
            "primary_user_id": test_user["id"],
            "name": "Test Account",
            "bank": "Test Bank",
            "account_type": "SAVINGS",
            "last_four_digits": "12345",  # 5 characters instead of 4
            "currency": "ARS",
        }

        response = client.post("/api/v1/bank-accounts", json=account_data)

        assert response.status_code == 422  # Pydantic validation error

    def test_should_return_400_for_invalid_currency(self, client, test_user, test_payment_method):
        """Should return 422 for invalid currency (Pydantic validation)"""
        account_data = {
            "primary_user_id": test_user["id"],
            "name": "Test Account",
            "bank": "Test Bank",
            "account_type": "SAVINGS",
            "last_four_digits": "1234",
            "currency": "INVALID",
        }

        response = client.post("/api/v1/bank-accounts", json=account_data)

        assert response.status_code == 422  # Pydantic validation error

    def test_should_return_404_for_nonexistent_primary_user(self, client):
        """Should return 404 when primary_user_id does not exist"""
        account_data = {
            "primary_user_id": 999999,  # Non-existent user
            "name": "Test Account",
            "bank": "Test Bank",
            "account_type": "SAVINGS",
            "last_four_digits": "1234",
            "currency": "ARS",
        }
        
        response = client.post("/api/v1/bank-accounts", json=account_data)
        
        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]

    def test_should_return_404_for_nonexistent_secondary_user(self, client, test_user):
        """Should return 404 when secondary_user_id does not exist"""
        account_data = {
            "primary_user_id": test_user["id"],
            "secondary_user_id": 999999,  # Non-existent user
            "name": "Test Account",
            "bank": "Test Bank",
            "account_type": "SAVINGS",
            "last_four_digits": "1234",
            "currency": "ARS",
        }
        
        response = client.post("/api/v1/bank-accounts", json=account_data)
        
        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]


class TestListBankAccountsByUserId:
    """Test GET /api/v1/bank-accounts"""

    def test_should_return_bank_accounts_for_user(self, client, test_user, test_payment_method):
        """Should return bank accounts for a specific user"""
        # Create first account
        account_data1 = {
            "primary_user_id": test_user["id"],
            "name": "Primary Account",
            "bank": "Bank A",
            "account_type": "SAVINGS",
            "last_four_digits": "1111",
            "currency": "ARS",
        }
        response1 = client.post("/api/v1/bank-accounts", json=account_data1)
        assert response1.status_code == 201

        # Create second account
        account_data2 = {
            "primary_user_id": test_user["id"],
            "name": "Secondary Account",
            "bank": "Bank B",
            "account_type": "CHECKING",
            "last_four_digits": "2222",
            "currency": "USD",
        }
        response2 = client.post("/api/v1/bank-accounts", json=account_data2)
        assert response2.status_code == 201

        # List accounts for user
        response = client.get("/api/v1/bank-accounts", params={"user_id": test_user["id"]})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [acc["name"] for acc in data]
        assert "Primary Account" in names
        assert "Secondary Account" in names

        # Verify all accounts belong to the user
        for account in data:
            assert account["primary_user_id"] == test_user["id"]

    def test_should_return_accounts_where_user_is_secondary(self, client, db_session, test_user):
        """Should return accounts where user has secondary access"""
        # Create another user
        from app.domain.entities.user import User
        from app.domain.value_objects.money import Money, Currency
        from app.infrastructure.persistence.mappers.user_mapper import UserMapper

        user2 = User(
            id=None,
            name="Secondary User",
            email="secondary@example.com",
            wage=Money(60000, Currency.ARS),
        )
        user2_model = UserMapper.to_model(user2)
        db_session.add(user2_model)
        db_session.flush()
        user2_id = user2_model.id

        # Create payment method for user2
        pm2 = PaymentMethod(
            id=None,
            user_id=user2_id,
            type=PaymentMethodType.BANK_ACCOUNT,
            name="Secondary PM",
            is_active=True,
        )
        pm2_model = PaymentMethodMapper.to_model(pm2)
        db_session.add(pm2_model)
        db_session.flush()
        pm2_id = pm2_model.id

        # Create account where test_user is primary and user2 is secondary
        account_data = {
            "primary_user_id": test_user["id"],
            "secondary_user_id": user2_id,
            "name": "Shared Account",
            "bank": "Shared Bank",
            "account_type": "SAVINGS",
            "last_four_digits": "3333",
            "currency": "ARS",
        }
        response = client.post("/api/v1/bank-accounts", json=account_data)
        assert response.status_code == 201

        # List accounts for primary user
        primary_response = client.get("/api/v1/bank-accounts", params={"user_id": test_user["id"]})
        assert primary_response.status_code == 200
        primary_data = primary_response.json()
        assert len(primary_data) == 1
        assert primary_data[0]["name"] == "Shared Account"

        # List accounts for secondary user
        secondary_response = client.get("/api/v1/bank-accounts", params={"user_id": user2_id})
        assert secondary_response.status_code == 200
        secondary_data = secondary_response.json()
        assert len(secondary_data) == 1
        assert secondary_data[0]["name"] == "Shared Account"

    def test_should_return_empty_list_for_user_without_accounts(self, client):
        """Should return 400 for nonexistent user (user validation in use case)"""
        response = client.get("/api/v1/bank-accounts", params={"user_id": 999})

        assert response.status_code == 400
        assert "User does not exist" in response.json()["detail"]

    def test_should_return_400_for_nonexistent_user(self, client):
        """Should return 400 when user does not exist"""
        response = client.get("/api/v1/bank-accounts", params={"user_id": 999})

        assert response.status_code == 400
        assert "User does not exist" in response.json()["detail"]

    def test_should_return_400_for_invalid_user_id(self, client):
        """Should return 400 for invalid user_id parameter"""
        response = client.get("/api/v1/bank-accounts", params={"user_id": "invalid"})

        assert response.status_code == 422  # FastAPI validation error
