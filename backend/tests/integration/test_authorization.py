"""
Authorization tests for the CashData API.

Tests that users can only access their own resources.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cashdata.infrastructure.api.main import app
from cashdata.infrastructure.persistence.models.user_model import Base
from cashdata.infrastructure.api.dependencies import get_session
from cashdata.domain.entities.user import User
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.infrastructure.persistence.mappers.user_mapper import UserMapper


@pytest.fixture
def db_engine():
    """Create in-memory SQLite engine for tests"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    """Create database session for tests"""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    """Create FastAPI test client with test database"""

    def override_get_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def create_user_in_db(db_session, name, email):
    """Helper function to create a user directly in the database"""
    user = User(id=None, name=name, email=email, wage=Money(50000, Currency.ARS))
    user_model = UserMapper.to_model(user)
    db_session.add(user_model)
    db_session.commit()
    db_session.refresh(user_model)
    return {"id": user_model.id, "name": user_model.name, "email": user_model.email}


@pytest.fixture
def two_users_setup(client, db_session):
    """Create two users with their own resources"""
    # User 1
    user1 = create_user_in_db(db_session, "User 1", "user1@example.com")

    # User 2
    user2 = create_user_in_db(db_session, "User 2", "user2@example.com")

    # Category (shared resource)
    category_data = {"name": "Test Category", "color": "#FF5733"}
    category_response = client.post("/api/v1/categories", json=category_data)
    category = category_response.json()

    # Credit card for User 1
    card1_data = {
        "name": "User 1 Card",
        "bank": "Bank 1",
        "last_four_digits": "1111",
        "billing_close_day": 15,
        "payment_due_day": 10,
    }
    card1_response = client.post(
        "/api/v1/credit-cards", json=card1_data, params={"user_id": user1["id"]}
    )
    card1 = card1_response.json()

    # Credit card for User 2
    card2_data = {
        "name": "User 2 Card",
        "bank": "Bank 2",
        "last_four_digits": "2222",
        "billing_close_day": 20,
        "payment_due_day": 15,
    }
    card2_response = client.post(
        "/api/v1/credit-cards", json=card2_data, params={"user_id": user2["id"]}
    )
    card2 = card2_response.json()

    # Purchase for User 1
    purchase1_data = {
        "credit_card_id": card1["id"],
        "category_id": category["id"],
        "purchase_date": "2025-01-15",
        "description": "User 1 Purchase",
        "total_amount": 1000.00,
        "total_currency": "ARS",
        "installments_count": 3,
    }
    purchase1_response = client.post(
        "/api/v1/purchases", json=purchase1_data, params={"user_id": user1["id"]}
    )
    purchase1 = purchase1_response.json()

    # Purchase for User 2
    purchase2_data = {
        "credit_card_id": card2["id"],
        "category_id": category["id"],
        "purchase_date": "2025-01-16",
        "description": "User 2 Purchase",
        "total_amount": 2000.00,
        "total_currency": "ARS",
        "installments_count": 2,
    }
    purchase2_response = client.post(
        "/api/v1/purchases", json=purchase2_data, params={"user_id": user2["id"]}
    )
    purchase2 = purchase2_response.json()

    return {
        "user1": user1,
        "user2": user2,
        "category": category,
        "card1": card1,
        "card2": card2,
        "purchase1": purchase1,
        "purchase2": purchase2,
    }


class TestPurchaseAuthorization:
    """Test authorization for purchase endpoints"""

    def test_user_cannot_access_other_user_purchase(self, client, two_users_setup):
        """User should not be able to access another user's purchase"""
        setup = two_users_setup

        # User 2 tries to access User 1's purchase
        response = client.get(
            f"/api/v1/purchases/{setup['purchase1']['id']}",
            params={"user_id": setup["user2"]["id"]},
        )

        # Should return 400 (purchase doesn't belong to user)
        assert response.status_code in [400, 404]

    def test_user_only_sees_own_purchases(self, client, two_users_setup):
        """User should only see their own purchases when listing"""
        setup = two_users_setup

        # User 1 lists purchases
        response1 = client.get(
            "/api/v1/purchases", params={"user_id": setup["user1"]["id"]}
        )
        purchases1 = response1.json()

        # Should only see User 1's purchase
        assert len(purchases1) == 1
        assert purchases1[0]["id"] == setup["purchase1"]["id"]

        # User 2 lists purchases
        response2 = client.get(
            "/api/v1/purchases", params={"user_id": setup["user2"]["id"]}
        )
        purchases2 = response2.json()

        # Should only see User 2's purchase
        assert len(purchases2) == 1
        assert purchases2[0]["id"] == setup["purchase2"]["id"]

    def test_user_cannot_access_other_user_installments(self, client, two_users_setup):
        """User should not be able to access installments of another user's purchase"""
        setup = two_users_setup

        # User 2 tries to access User 1's installments
        response = client.get(
            f"/api/v1/purchases/{setup['purchase1']['id']}/installments",
            params={"user_id": setup["user2"]["id"]},
        )

        # Should return 400 or 404
        assert response.status_code in [400, 404]


class TestCreditCardAuthorization:
    """Test authorization for credit card endpoints"""

    def test_user_cannot_access_other_user_card(self, client, two_users_setup):
        """User should not be able to access another user's credit card"""
        setup = two_users_setup

        # User 2 tries to access User 1's card
        response = client.get(
            f"/api/v1/credit-cards/{setup['card1']['id']}",
            params={"user_id": setup["user2"]["id"]},
        )

        # Should return 404
        assert response.status_code == 404

    def test_user_only_sees_own_cards(self, client, two_users_setup):
        """User should only see their own credit cards when listing"""
        setup = two_users_setup

        # User 1 lists cards
        response1 = client.get(
            "/api/v1/credit-cards", params={"user_id": setup["user1"]["id"]}
        )
        cards1 = response1.json()

        # Should only see User 1's card
        assert len(cards1) == 1
        assert cards1[0]["id"] == setup["card1"]["id"]

        # User 2 lists cards
        response2 = client.get(
            "/api/v1/credit-cards", params={"user_id": setup["user2"]["id"]}
        )
        cards2 = response2.json()

        # Should only see User 2's card
        assert len(cards2) == 1
        assert cards2[0]["id"] == setup["card2"]["id"]

    def test_user_cannot_access_other_user_card_summary(self, client, two_users_setup):
        """User should not be able to access summary of another user's card"""
        setup = two_users_setup

        # User 2 tries to access User 1's card summary
        response = client.get(
            f"/api/v1/credit-cards/{setup['card1']['id']}/summary",
            params={"user_id": setup["user2"]["id"], "billing_period": "202501"},
        )

        # Should return 400 or 404
        assert response.status_code in [400, 404]

    def test_user_cannot_see_other_user_purchases_by_card(
        self, client, two_users_setup
    ):
        """User should not be able to see purchases of another user's card"""
        setup = two_users_setup

        # User 2 tries to list User 1's card purchases
        response = client.get(
            f"/api/v1/credit-cards/{setup['card1']['id']}/purchases",
            params={"user_id": setup["user2"]["id"]},
        )

        # Should return 400 or 404
        assert response.status_code in [400, 404]


class TestCategoryAuthorizationForPurchases:
    """Test that category purchases are filtered by user"""

    def test_category_purchases_filtered_by_user(self, client, two_users_setup):
        """Category purchases should be filtered by requesting user"""
        setup = two_users_setup

        # User 1 requests category purchases
        response1 = client.get(
            f"/api/v1/categories/{setup['category']['id']}/purchases",
            params={"user_id": setup["user1"]["id"]},
        )
        purchases1 = response1.json()

        # Should only see User 1's purchase
        assert len(purchases1) == 1
        assert purchases1[0]["description"] == "User 1 Purchase"

        # User 2 requests category purchases
        response2 = client.get(
            f"/api/v1/categories/{setup['category']['id']}/purchases",
            params={"user_id": setup["user2"]["id"]},
        )
        purchases2 = response2.json()

        # Should only see User 2's purchase
        assert len(purchases2) == 1
        assert purchases2[0]["description"] == "User 2 Purchase"


class TestCrossUserIsolation:
    """Test complete isolation between users"""

    def test_complete_user_isolation(self, client, two_users_setup):
        """Verify complete isolation between users across all endpoints"""
        setup = two_users_setup
        user1_id = setup["user1"]["id"]
        user2_id = setup["user2"]["id"]

        # User 1's view
        user1_purchases = client.get(
            "/api/v1/purchases", params={"user_id": user1_id}
        ).json()

        user1_cards = client.get(
            "/api/v1/credit-cards", params={"user_id": user1_id}
        ).json()

        user1_category_purchases = client.get(
            f"/api/v1/categories/{setup['category']['id']}/purchases",
            params={"user_id": user1_id},
        ).json()

        # Verify User 1 only sees their own data
        assert len(user1_purchases) == 1
        assert user1_purchases[0]["user_id"] == user1_id
        assert len(user1_cards) == 1
        assert user1_cards[0]["user_id"] == user1_id
        assert len(user1_category_purchases) == 1
        assert user1_category_purchases[0]["user_id"] == user1_id

        # User 2's view
        user2_purchases = client.get(
            "/api/v1/purchases", params={"user_id": user2_id}
        ).json()

        user2_cards = client.get(
            "/api/v1/credit-cards", params={"user_id": user2_id}
        ).json()

        user2_category_purchases = client.get(
            f"/api/v1/categories/{setup['category']['id']}/purchases",
            params={"user_id": user2_id},
        ).json()

        # Verify User 2 only sees their own data
        assert len(user2_purchases) == 1
        assert user2_purchases[0]["user_id"] == user2_id
        assert len(user2_cards) == 1
        assert user2_cards[0]["user_id"] == user2_id
        assert len(user2_category_purchases) == 1
        assert user2_category_purchases[0]["user_id"] == user2_id

        # Verify no overlap
        assert user1_purchases[0]["id"] != user2_purchases[0]["id"]
        assert user1_cards[0]["id"] != user2_cards[0]["id"]
