"""
API integration tests for monthly statements endpoints.

Tests all monthly statement-related API endpoints with real database and FastAPI test client.
"""

import pytest


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
def test_statement(client, test_user, test_credit_card):
    """Create a test monthly statement"""
    statement_data = {
        "credit_card_id": test_credit_card["id"],
        "start_date": "2025-01-01",
        "closing_date": "2025-01-15",
        "due_date": "2025-01-20",
    }

    response = client.post(
        "/api/v1/statements", json=statement_data, params={"user_id": test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


class TestGetStatementsByCard:
    """Test GET /api/v1/statements/by-card/{credit_card_id}"""

    def test_get_statements_by_card_returns_200(
        self, client, test_user, test_credit_card, test_statement
    ):
        """Should return statements for the credit card successfully"""
        response = client.get(
            f"/api/v1/statements/by-card/{test_credit_card['id']}",
            params={"user_id": test_user["id"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Check structure of first statement
        statement = data[0]
        assert "id" in statement
        assert "credit_card_id" in statement
        assert "credit_card_name" in statement
        assert "start_date" in statement
        assert "closing_date" in statement
        assert "due_date" in statement

        # Verify it belongs to the correct credit card
        assert statement["credit_card_id"] == test_credit_card["id"]
        assert statement["credit_card_name"] == test_credit_card["name"]

    def test_get_statements_by_card_includes_future_statements(
        self, client, test_user, test_credit_card
    ):
        """Should include future statements in the result (no upper bound on due_date)"""
        future_statement_data = {
            "credit_card_id": test_credit_card["id"],
            "start_date": "2030-01-01",
            "closing_date": "2030-01-30",
            "due_date": "2030-02-10",
        }

        create_resp = client.post(
            "/api/v1/statements", json=future_statement_data, params={"user_id": test_user["id"]}
        )
        assert create_resp.status_code == 201
        future_stmt = create_resp.json()

        response = client.get(
            f"/api/v1/statements/by-card/{test_credit_card['id']}",
            params={"user_id": test_user["id"]}
        )
        assert response.status_code == 200
        data = response.json()
        ids = [s["id"] for s in data]
        assert future_stmt["id"] in ids

    def test_get_statements_by_card_wrong_user_returns_404(
        self, client, test_user, test_credit_card, test_statement
    ):
        """Should return 404 when user doesn't own the credit card"""
        response = client.get(
            f"/api/v1/statements/by-card/{test_credit_card['id']}",
            params={"user_id": 999}  # Wrong user
        )

        assert response.status_code == 404

    def test_get_statements_by_card_invalid_card_returns_404(
        self, client, test_user
    ):
        """Should return 404 for non-existent credit card"""
        response = client.get(
            "/api/v1/statements/by-card/999",
            params={"user_id": test_user["id"]}
        )

        assert response.status_code == 404

    def test_get_statements_by_card_empty_list(
        self, client, test_user, test_credit_card
    ):
        """Should return empty list when credit card has no statements"""
        # Create a new credit card without statements
        card_data = {
            "name": "Empty Card",
            "bank": "Test Bank",
            "last_four_digits": "5678",
            "billing_close_day": 20,
            "payment_due_day": 15,
            "credit_limit_amount": 5000.00,
            "credit_limit_currency": "ARS",
        }
        card_response = client.post(
            "/api/v1/credit-cards", json=card_data, params={"user_id": test_user["id"]}
        )
        assert card_response.status_code == 201
        new_card = card_response.json()

        # Get statements for the new card
        response = client.get(
            f"/api/v1/statements/by-card/{new_card['id']}",
            params={"user_id": test_user["id"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0