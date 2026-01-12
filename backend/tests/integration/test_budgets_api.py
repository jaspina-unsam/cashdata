"""
API integration tests for budgets endpoints.

Tests all budget-related API endpoints with real database and FastAPI test client.
"""

import pytest

from app.domain.entities.user import User
from app.domain.value_objects.money import Money, Currency
from app.infrastructure.persistence.mappers.user_mapper import UserMapper


@pytest.fixture
def test_users(db_session):
    """Create test users directly in database"""
    users = []
    for i in range(1, 4):  # Create users 1, 2, 3
        user = User(
            id=None,
            name=f"Test User {i}",
            email=f"user{i}@example.com",
            wage=Money(50000 + i * 5000, Currency.ARS),
        )
        user_model = UserMapper.to_model(user)
        db_session.add(user_model)
        db_session.commit()
        db_session.refresh(user_model)
        users.append({"id": user_model.id, "name": user_model.name, "email": user_model.email})
    return users


class TestCreateBudget:
    """Test POST /api/v1/budgets"""

    def test_should_create_budget_with_multiple_participants(self, client, test_users):
        """Should create a budget with multiple participants"""
        budget_data = {
            "name": "January 2026 Budget",
            "year": 2026,
            "month": 1,
            "description": "Shared household budget",
            "created_by_user_id": test_users[0]["id"],
            "participant_user_ids": [test_users[0]["id"], test_users[1]["id"]]
        }

        response = client.post("/api/v1/budgets", json=budget_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "January 2026 Budget"
        assert data["period"] == "202601"
        assert data["description"] == "Shared household budget"
        assert data["status"] == "active"
        assert data["created_by_user_id"] == test_users[0]["id"]
        assert data["participant_count"] == 2
        assert "id" in data
        assert "created_at" in data

    def test_should_create_budget_with_single_participant(self, client, test_users):
        """Should create a budget with single participant"""
        budget_data = {
            "name": "Personal Budget",
            "year": 2026,
            "month": 2,
            "created_by_user_id": test_users[0]["id"],
            "participant_user_ids": [test_users[0]["id"]]
        }

        response = client.post("/api/v1/budgets", json=budget_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Personal Budget"
        assert data["period"] == "202602"
        assert data["participant_count"] == 1

    def test_should_fail_when_creator_not_participant(self, client, test_users):
        """Should fail when creator is not included in participants"""
        budget_data = {
            "name": "Invalid Budget",
            "year": 2026,
            "month": 1,
            "created_by_user_id": test_users[0]["id"],
            "participant_user_ids": [test_users[1]["id"]]  # Creator not included
        }

        response = client.post("/api/v1/budgets", json=budget_data)

        assert response.status_code == 409
        assert "creator must be a participant" in response.json()["detail"].lower()

    def test_should_fail_when_creator_not_found(self, client, test_users):
        """Should fail when creator user doesn't exist"""
        budget_data = {
            "name": "Invalid Budget",
            "year": 2026,
            "month": 1,
            "created_by_user_id": 999,  # Non-existent user
            "participant_user_ids": [999]
        }

        response = client.post("/api/v1/budgets", json=budget_data)

        assert response.status_code == 404
        assert "creator user with id 999 not found" in response.json()["detail"].lower()

    def test_should_fail_when_participant_not_found(self, client, test_users):
        """Should fail when participant user doesn't exist"""
        budget_data = {
            "name": "Invalid Budget",
            "year": 2026,
            "month": 1,
            "created_by_user_id": test_users[0]["id"],
            "participant_user_ids": [test_users[0]["id"], 999]  # One participant doesn't exist
        }

        response = client.post("/api/v1/budgets", json=budget_data)

        assert response.status_code == 404
        assert "participant user with id 999 not found" in response.json()["detail"].lower()

    def test_should_fail_when_duplicate_participants(self, client, test_users):
        """Should fail when participant user IDs are duplicated"""
        budget_data = {
            "name": "Invalid Budget",
            "year": 2026,
            "month": 1,
            "created_by_user_id": test_users[0]["id"],
            "participant_user_ids": [test_users[0]["id"], test_users[0]["id"]]  # Duplicate
        }

        response = client.post("/api/v1/budgets", json=budget_data)

        assert response.status_code == 409
        assert "duplicate participant user ids" in response.json()["detail"].lower()

    def test_should_fail_when_budget_already_exists_for_period_and_creator(self, client, test_users):
        """Should fail when budget already exists for same period and creator"""
        # Create first budget
        budget_data = {
            "name": "January Budget",
            "year": 2026,
            "month": 1,
            "created_by_user_id": test_users[0]["id"],
            "participant_user_ids": [test_users[0]["id"]]
        }
        response1 = client.post("/api/v1/budgets", json=budget_data)
        assert response1.status_code == 201

        # Try to create another budget for same period and creator
        budget_data2 = {
            "name": "Another January Budget",
            "year": 2026,
            "month": 1,
            "created_by_user_id": test_users[0]["id"],
            "participant_user_ids": [test_users[0]["id"]]
        }
        response2 = client.post("/api/v1/budgets", json=budget_data2)

        assert response2.status_code == 409
        assert "budget already exists" in response2.json()["detail"].lower()


class TestListBudgets:
    """Test GET /api/v1/budgets"""

    def test_should_list_budgets_for_user_in_period(self, client, test_users):
        """Should list budgets where user is participant for specific period"""
        # Create budgets
        budget1_data = {
            "name": "January Budget 1",
            "year": 2026,
            "month": 1,
            "created_by_user_id": test_users[0]["id"],
            "participant_user_ids": [test_users[0]["id"], test_users[1]["id"]]
        }
        budget2_data = {
            "name": "January Budget 2",
            "year": 2026,
            "month": 1,
            "created_by_user_id": test_users[1]["id"],
            "participant_user_ids": [test_users[1]["id"], test_users[2]["id"]]
        }
        budget3_data = {
            "name": "February Budget",
            "year": 2026,
            "month": 2,
            "created_by_user_id": test_users[0]["id"],
            "participant_user_ids": [test_users[0]["id"]]
        }

        client.post("/api/v1/budgets", json=budget1_data)
        client.post("/api/v1/budgets", json=budget2_data)
        client.post("/api/v1/budgets", json=budget3_data)

        # List budgets for user 1 in January 2026
        response = client.get("/api/v1/budgets", params={"period": "202601", "user_id": test_users[0]["id"]})

        assert response.status_code == 200
        budgets = response.json()
        assert len(budgets) == 1  # Only budget1 includes user 1
        assert budgets[0]["name"] == "January Budget 1"
        assert budgets[0]["participant_count"] == 2

    def test_should_return_empty_list_when_no_budgets_for_period(self, client, test_users):
        """Should return empty list when no budgets exist for period"""
        response = client.get("/api/v1/budgets", params={"period": "202601", "user_id": test_users[0]["id"]})

        assert response.status_code == 200
        budgets = response.json()
        assert len(budgets) == 0

    def test_should_fail_for_invalid_period_format(self, client, test_users):
        """Should fail for invalid period format"""
        response = client.get("/api/v1/budgets", params={"period": "invalid", "user_id": test_users[0]["id"]})

        assert response.status_code == 422  # FastAPI validation error


class TestGetBudgetDetails:
    """Test GET /api/v1/budgets/{budget_id}"""

    def test_should_get_budget_details_for_participant(self, client, test_users):
        """Should return budget details for authorized participant"""
        # Create budget
        budget_data = {
            "name": "Test Budget",
            "year": 2026,
            "month": 1,
            "description": "Budget for testing",
            "created_by_user_id": test_users[0]["id"],
            "participant_user_ids": [test_users[0]["id"], test_users[1]["id"]]
        }
        create_response = client.post("/api/v1/budgets", json=budget_data)
        budget_id = create_response.json()["id"]

        # Get budget details as participant
        response = client.get(f"/api/v1/budgets/{budget_id}", params={"user_id": test_users[1]["id"]})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == budget_id
        assert data["name"] == "Test Budget"
        assert data["participant_count"] == 2

    def test_should_fail_when_budget_not_found(self, client, test_users):
        """Should fail when budget doesn't exist"""
        response = client.get("/api/v1/budgets/999", params={"user_id": test_users[0]["id"]})

        assert response.status_code == 404
        assert "budget with id 999 not found" in response.json()["detail"].lower()

    def test_should_fail_when_user_not_participant(self, client, test_users):
        """Should fail when user is not a participant"""
        # Create budget with only user 1 and 2
        budget_data = {
            "name": "Exclusive Budget",
            "year": 2026,
            "month": 1,
            "created_by_user_id": test_users[0]["id"],
            "participant_user_ids": [test_users[0]["id"], test_users[1]["id"]]
        }
        create_response = client.post("/api/v1/budgets", json=budget_data)
        budget_id = create_response.json()["id"]

        # Try to access as user 3 (not a participant)
        response = client.get(f"/api/v1/budgets/{budget_id}", params={"user_id": test_users[2]["id"]})

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()