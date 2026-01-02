"""
End-to-end flow tests for the CashData API.

Tests complete user workflows from start to finish.
"""

import pytest
from datetime import date

from cashdata.domain.entities.user import User
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.infrastructure.persistence.mappers.user_mapper import UserMapper


def create_user_in_db(db_session, name, email):
    """Helper function to create a user directly in the database"""
    user = User(id=None, name=name, email=email, wage=Money(50000, Currency.ARS))
    user_model = UserMapper.to_model(user)
    db_session.add(user_model)
    db_session.commit()
    db_session.refresh(user_model)
    return {"id": user_model.id, "name": user_model.name, "email": user_model.email}


class TestCompletePurchaseFlow:
    """Test complete purchase workflow from creation to summary"""

    def test_complete_purchase_and_summary_flow(self, client, db_session):
        """
        Complete flow:
        1. Create user
        2. Create category
        3. Create credit card
        4. Create purchase with multiple installments
        5. Get purchase details
        6. Get installments for purchase
        7. Get credit card summary
        """
        # 1. Create user
        user = create_user_in_db(db_session, "John Doe", "john@example.com")
        user_id = user["id"]

        # 2. Create category
        category_data = {"name": "Electronics", "color": "#3357FF"}
        category_response = client.post("/api/v1/categories", json=category_data)
        assert category_response.status_code == 201
        category = category_response.json()
        category_id = category["id"]

        # 3. Create credit card
        card_data = {
            "name": "Visa Gold",
            "bank": "Test Bank",
            "last_four_digits": "1234",
            "billing_close_day": 15,
            "payment_due_day": 10,
            "credit_limit_amount": 100000.00,
            "credit_limit_currency": "ARS",
        }
        card_response = client.post(
            "/api/v1/credit-cards", json=card_data, params={"user_id": user_id}
        )
        assert card_response.status_code == 201
        card = card_response.json()
        card_id = card["id"]

        # 4. Create purchase with 6 installments
        purchase_data = {
            "credit_card_id": card_id,
            "category_id": category_id,
            "purchase_date": "2025-01-10",
            "description": "New Laptop",
            "total_amount": 60000.00,
            "total_currency": "ARS",
            "installments_count": 6,
        }
        purchase_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": user_id}
        )
        assert purchase_response.status_code == 201
        purchase = purchase_response.json()
        purchase_id = purchase["id"]

        # Verify purchase details
        assert purchase["description"] == "New Laptop"
        assert purchase["total_amount"] == "60000.00"
        assert purchase["installments_count"] == 6

        # 5. Get purchase details
        get_purchase_response = client.get(
            f"/api/v1/purchases/{purchase_id}", params={"user_id": user_id}
        )
        assert get_purchase_response.status_code == 200
        retrieved_purchase = get_purchase_response.json()
        assert retrieved_purchase["id"] == purchase_id
        assert retrieved_purchase["description"] == "New Laptop"

        # 6. Get installments for purchase
        installments_response = client.get(
            f"/api/v1/purchases/{purchase_id}/installments", params={"user_id": user_id}
        )
        assert installments_response.status_code == 200
        installments = installments_response.json()

        # Verify installments
        assert len(installments) == 6
        assert installments[0]["installment_number"] == 1
        assert installments[5]["installment_number"] == 6

        # Verify installment amounts (60000 / 6 = 10000 each)
        assert installments[0]["amount"] == "10000.00"
        assert installments[1]["amount"] == "10000.00"

        # 7. Get credit card summary for February 2025
        summary_response = client.get(
            f"/api/v1/credit-cards/{card_id}/summary",
            params={"user_id": user_id, "billing_period": "202502"},
        )
        assert summary_response.status_code == 200
        summary = summary_response.json()

        # Verify summary
        assert summary["credit_card_id"] == card_id
        assert summary["billing_period"] == "202502"
        assert len(summary["installments"]) > 0
        assert float(summary["total_amount"]) > 0


class TestMultiplePurchasesFlow:
    """Test flow with multiple purchases and filtering"""

    def test_multiple_purchases_and_filtering(self, client, db_session):
        """
        Flow:
        1. Create user with credit card and categories
        2. Create multiple purchases
        3. Filter by date range
        4. Filter by credit card
        5. Filter by category
        """
        # 1. Setup: Create user
        user = create_user_in_db(db_session, "Jane Smith", "jane@example.com")
        user_id = user["id"]

        # Create credit card
        card_data = {
            "name": "Mastercard",
            "bank": "Test Bank",
            "last_four_digits": "5678",
            "billing_close_day": 20,
            "payment_due_day": 15,
        }
        card_response = client.post(
            "/api/v1/credit-cards", json=card_data, params={"user_id": user_id}
        )
        card_id = card_response.json()["id"]

        # Create categories
        categories = []
        for name in ["Food", "Transport", "Entertainment"]:
            cat_response = client.post(
                "/api/v1/categories", json={"name": name, "color": "#FF5733"}
            )
            categories.append(cat_response.json())

        # 2. Create multiple purchases
        purchases_data = [
            {
                "date": "2025-01-05",
                "description": "Grocery shopping",
                "amount": 5000.00,
                "category_id": categories[0]["id"],  # Food
            },
            {
                "date": "2025-01-15",
                "description": "Taxi ride",
                "amount": 2000.00,
                "category_id": categories[1]["id"],  # Transport
            },
            {
                "date": "2025-01-25",
                "description": "Movie tickets",
                "amount": 3000.00,
                "category_id": categories[2]["id"],  # Entertainment
            },
        ]

        for p in purchases_data:
            purchase_data = {
                "credit_card_id": card_id,
                "category_id": p["category_id"],
                "purchase_date": p["date"],
                "description": p["description"],
                "total_amount": p["amount"],
                "total_currency": "ARS",
                "installments_count": 1,
            }
            response = client.post(
                "/api/v1/purchases", json=purchase_data, params={"user_id": user_id}
            )
            assert response.status_code == 201

        # 3. Filter by date range (middle purchase only)
        date_filter_response = client.get(
            "/api/v1/purchases",
            params={
                "user_id": user_id,
                "start_date": "2025-01-10",
                "end_date": "2025-01-20",
            },
        )
        assert date_filter_response.status_code == 200
        date_filtered = date_filter_response.json()
        assert len(date_filtered) == 1
        assert date_filtered[0]["description"] == "Taxi ride"

        # 4. Filter by credit card
        card_purchases_response = client.get(
            f"/api/v1/credit-cards/{card_id}/purchases", params={"user_id": user_id}
        )
        assert card_purchases_response.status_code == 200
        card_purchases = card_purchases_response.json()
        assert len(card_purchases) == 3

        # 5. Filter by category
        food_purchases_response = client.get(
            f"/api/v1/categories/{categories[0]['id']}/purchases",
            params={"user_id": user_id},
        )
        assert food_purchases_response.status_code == 200
        food_purchases = food_purchases_response.json()
        assert len(food_purchases) == 1
        assert food_purchases[0]["description"] == "Grocery shopping"


class TestInstallmentGenerationFlow:
    """Test installment generation across billing periods"""

    def test_installments_across_multiple_billing_periods(self, client, db_session):
        """
        Test that installments are properly distributed across billing periods
        """
        # Setup
        user = create_user_in_db(db_session, "Test User", "test@example.com")
        user_id = user["id"]

        category_data = {"name": "Test", "color": "#FF5733"}
        category_response = client.post("/api/v1/categories", json=category_data)
        category_id = category_response.json()["id"]

        card_data = {
            "name": "Test Card",
            "bank": "Test Bank",
            "last_four_digits": "1234",
            "billing_close_day": 15,
            "payment_due_day": 10,
        }
        card_response = client.post(
            "/api/v1/credit-cards", json=card_data, params={"user_id": user_id}
        )
        card_id = card_response.json()["id"]

        # Create purchase with 12 installments
        purchase_data = {
            "credit_card_id": card_id,
            "category_id": category_id,
            "purchase_date": "2025-01-10",
            "description": "Annual subscription",
            "total_amount": 120000.00,
            "total_currency": "ARS",
            "installments_count": 12,
        }
        purchase_response = client.post(
            "/api/v1/purchases", json=purchase_data, params={"user_id": user_id}
        )
        purchase_id = purchase_response.json()["id"]

        # Get all installments
        installments_response = client.get(
            f"/api/v1/purchases/{purchase_id}/installments", params={"user_id": user_id}
        )
        installments = installments_response.json()

        # Verify 12 installments
        assert len(installments) == 12

        # Verify each installment amount (120000 / 12 = 10000)
        for inst in installments:
            assert inst["amount"] == "10000.00"

        # Check different billing periods have installments
        billing_periods = set(inst["billing_period"] for inst in installments)
        assert len(billing_periods) == 12  # 12 different months

        # Check first billing period summary
        first_period = installments[0]["billing_period"]
        summary_response = client.get(
            f"/api/v1/credit-cards/{card_id}/summary",
            params={"user_id": user_id, "billing_period": first_period},
        )
        summary = summary_response.json()
        assert summary["installments_count"] >= 1


class TestPaginationFlow:
    """Test pagination across different endpoints"""

    def test_pagination_with_large_dataset(self, client, db_session):
        """Test pagination when there are many records"""
        # Setup
        user = create_user_in_db(db_session, "Test User", "test@example.com")
        user_id = user["id"]

        # Create 20 credit cards
        card_ids = []
        for i in range(20):
            card_data = {
                "name": f"Card {i+1}",
                "bank": "Test Bank",
                "last_four_digits": f"{i:04d}",
                "billing_close_day": 15,
                "payment_due_day": 10,
            }
            response = client.post(
                "/api/v1/credit-cards", json=card_data, params={"user_id": user_id}
            )
            card_ids.append(response.json()["id"])

        # Test pagination
        # Page 1: First 10 cards
        page1_response = client.get(
            "/api/v1/credit-cards", params={"user_id": user_id, "skip": 0, "limit": 10}
        )
        page1 = page1_response.json()
        assert len(page1) == 10

        # Page 2: Next 10 cards
        page2_response = client.get(
            "/api/v1/credit-cards", params={"user_id": user_id, "skip": 10, "limit": 10}
        )
        page2 = page2_response.json()
        assert len(page2) == 10

        # Page 3: No more cards
        page3_response = client.get(
            "/api/v1/credit-cards", params={"user_id": user_id, "skip": 20, "limit": 10}
        )
        page3 = page3_response.json()
        assert len(page3) == 0

        # Verify no duplicates
        page1_ids = [c["id"] for c in page1]
        page2_ids = [c["id"] for c in page2]
        assert len(set(page1_ids) & set(page2_ids)) == 0
