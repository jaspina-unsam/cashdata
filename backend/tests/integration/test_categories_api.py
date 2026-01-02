"""
API integration tests for categories endpoints.

Tests all category-related API endpoints with real database and FastAPI test client.
"""

import pytest

from cashdata.domain.entities.user import User
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.infrastructure.persistence.mappers.user_mapper import UserMapper


@pytest.fixture
def test_credit_card(client, test_user):
    """Create a test credit card"""
    card_data = {
        "name": "Test Card",
        "bank": "Test Bank",
        "last_four_digits": "1234",
        "billing_close_day": 15,
        "payment_due_day": 10,
    }
    response = client.post(
        "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


class TestCreateCategory:
    """Test POST /api/v1/categories"""

    def test_should_create_category(self, client):
        """Should create a category"""
        category_data = {"name": "Food", "color": "#FF5733"}

        response = client.post("/api/v1/categories", json=category_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Food"
        assert data["color"] == "#FF5733"
        assert "id" in data

    def test_should_validate_color_format(self, client):
        """Should validate hex color format"""
        invalid_category = {"name": "Invalid", "color": "not-a-hex-color"}

        response = client.post("/api/v1/categories", json=invalid_category)

        assert response.status_code == 422  # Validation error


class TestListCategories:
    """Test GET /api/v1/categories"""

    def test_should_list_all_categories(self, client):
        """Should list all categories"""
        # Create multiple categories
        categories = [
            {"name": "Food", "color": "#FF5733"},
            {"name": "Transport", "color": "#33FF57"},
            {"name": "Entertainment", "color": "#3357FF"},
        ]

        for cat in categories:
            client.post("/api/v1/categories", json=cat)

        # List categories
        response = client.get("/api/v1/categories")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # At least the ones we created

    def test_should_return_empty_list_when_no_categories(self, client):
        """Should return empty list when no categories exist"""
        response = client.get("/api/v1/categories")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestGetCategoryById:
    """Test GET /api/v1/categories/{category_id}"""

    def test_should_return_category_by_id(self, client):
        """Should retrieve category by ID"""
        # Create category
        category_data = {"name": "Test Category", "color": "#FF5733"}
        create_response = client.post("/api/v1/categories", json=category_data)
        category_id = create_response.json()["id"]

        # Get category
        response = client.get(f"/api/v1/categories/{category_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == "Test Category"
        assert data["color"] == "#FF5733"

    def test_should_return_404_for_nonexistent_category(self, client):
        """Should return 404 for non-existent category"""
        response = client.get("/api/v1/categories/999")

        assert response.status_code == 404


class TestListPurchasesByCategory:
    """Test GET /api/v1/categories/{category_id}/purchases"""

    def test_should_list_purchases_for_category(
        self, client, test_user, test_credit_card
    ):
        """Should list all purchases for a category"""
        # Create category
        category_data = {"name": "Food", "color": "#FF5733"}
        category_response = client.post("/api/v1/categories", json=category_data)
        category_id = category_response.json()["id"]

        # Create multiple purchases
        for i in range(3):
            purchase_data = {
                "credit_card_id": test_credit_card["id"],
                "category_id": category_id,
                "purchase_date": f"2025-01-{15+i}",
                "description": f"Food Purchase {i+1}",
                "total_amount": 1000.00 * (i + 1),
                "total_currency": "ARS",
                "installments_count": 1,
            }
            client.post(
                "/api/v1/purchases",
                json=purchase_data,
                params={"user_id": test_user["id"]},
            )

        # List purchases for category
        response = client.get(
            f"/api/v1/categories/{category_id}/purchases",
            params={"user_id": test_user["id"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # All purchases should belong to this category
        for purchase in data:
            assert purchase["category_id"] == category_id

    def test_should_return_empty_list_when_no_purchases(self, client, test_user):
        """Should return empty list when category has no purchases"""
        # Create category without purchases
        category_data = {"name": "Empty Category", "color": "#FF5733"}
        category_response = client.post("/api/v1/categories", json=category_data)
        category_id = category_response.json()["id"]

        response = client.get(
            f"/api/v1/categories/{category_id}/purchases",
            params={"user_id": test_user["id"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_should_return_404_for_nonexistent_category(self, client, test_user):
        """Should return 404 for non-existent category"""
        response = client.get(
            "/api/v1/categories/999/purchases", params={"user_id": test_user["id"]}
        )

        assert response.status_code == 404

    def test_should_only_return_purchases_for_user(
        self, client, test_user, test_credit_card, db_session
    ):
        """Should only return purchases belonging to the requesting user"""
        # Create another user
        user2 = User(
            id=None,
            name="User 2",
            email="user2@example.com",
            wage=Money(60000, Currency.ARS),
        )
        user2_model = UserMapper.to_model(user2)
        db_session.add(user2_model)
        db_session.commit()
        db_session.refresh(user2_model)
        user2 = {
            "id": user2_model.id,
            "name": user2_model.name,
            "email": user2_model.email,
        }

        # Create card for user2
        card2_data = {
            "name": "User 2 Card",
            "bank": "Test Bank",
            "last_four_digits": "5678",
            "billing_close_day": 15,
            "payment_due_day": 10,
        }
        card2_response = client.post(
            "/api/v1/credit-cards", json=card2_data, params={"user_id": user2["id"]}
        )
        card2 = card2_response.json()

        # Create category
        category_data = {"name": "Shared Category", "color": "#FF5733"}
        category_response = client.post("/api/v1/categories", json=category_data)
        category_id = category_response.json()["id"]

        # Create purchases for both users in same category
        purchase1_data = {
            "credit_card_id": test_credit_card["id"],
            "category_id": category_id,
            "purchase_date": "2025-01-15",
            "description": "User 1 Purchase",
            "total_amount": 1000.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }
        client.post(
            "/api/v1/purchases",
            json=purchase1_data,
            params={"user_id": test_user["id"]},
        )

        purchase2_data = {
            "credit_card_id": card2["id"],
            "category_id": category_id,
            "purchase_date": "2025-01-16",
            "description": "User 2 Purchase",
            "total_amount": 2000.00,
            "total_currency": "ARS",
            "installments_count": 1,
        }
        client.post(
            "/api/v1/purchases", json=purchase2_data, params={"user_id": user2["id"]}
        )

        # User 1 should only see their purchase
        response = client.get(
            f"/api/v1/categories/{category_id}/purchases",
            params={"user_id": test_user["id"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["description"] == "User 1 Purchase"
