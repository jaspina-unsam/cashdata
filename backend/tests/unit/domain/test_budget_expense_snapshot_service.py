# backend/tests/unit/domain/test_budget_expense_snapshot_service.py
import pytest
from datetime import date
from app.domain.services.budget_expense_snapshot_service import BudgetExpenseSnapshotService, ExpenseSnapshot
from app.domain.entities.purchase import Purchase
from app.domain.entities.installment import Installment
from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.money import Money
from app.domain.value_objects.payment_method_type import PaymentMethodType


class TestBudgetExpenseSnapshotService:
    """Tests para BudgetExpenseSnapshotService"""

    def test_create_snapshot_from_purchase_should_capture_all_data(self):
        service = BudgetExpenseSnapshotService()

        purchase = Purchase(
            id=1,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2026, 1, 15),
            description="Supermercado Carrefour",
            total_amount=Money(12500, "ARS"),
            installments_count=1
        )

        payment_method = PaymentMethod(
            id=1,
            user_id=1,
            type=PaymentMethodType.CREDIT_CARD,
            name="Visa Gold",
            is_active=True,
            created_at=None,
            updated_at=None
        )

        snapshot = service.create_snapshot_from_purchase(purchase, payment_method)

        assert snapshot.amount == Money(12500, "ARS")
        assert snapshot.currency == "ARS"
        assert snapshot.description == "Supermercado Carrefour"
        assert snapshot.date == date(2026, 1, 15)
        assert snapshot.payment_method_name == "Visa Gold"

    def test_create_snapshot_from_purchase_without_payment_method(self):
        service = BudgetExpenseSnapshotService()

        purchase = Purchase(
            id=1,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2026, 1, 15),
            description="Café",
            total_amount=Money(800, "ARS"),
            installments_count=1
        )

        snapshot = service.create_snapshot_from_purchase(purchase, None)

        assert snapshot.payment_method_name is None

    def test_create_snapshot_from_installment_should_capture_all_data(self):
        service = BudgetExpenseSnapshotService()

        installment = Installment(
            id=1,
            purchase_id=1,
            installment_number=1,
            total_installments=12,
            amount=Money(3800, "ARS"),
            billing_period="202601",
            manually_assigned_statement_id=None
        )

        payment_method = PaymentMethod(
            id=2,
            user_id=1,
            type=PaymentMethodType.DIGITAL_WALLET,
            name="Mercado Pago",
            is_active=True,
            created_at=None,
            updated_at=None
        )

        snapshot = service.create_snapshot_from_installment(installment, payment_method)

        assert snapshot.amount == Money(3800, "ARS")
        assert snapshot.currency == "ARS"
        assert snapshot.description == "Installment 1/12"
        assert snapshot.date == date(2026, 1, 1)  # First day of billing period
        assert snapshot.payment_method_name == "Mercado Pago"

    def test_create_snapshot_from_installment_without_payment_method(self):
        service = BudgetExpenseSnapshotService()

        installment = Installment(
            id=1,
            purchase_id=1,
            installment_number=2,
            total_installments=12,
            amount=Money(3800, "ARS"),
            billing_period="202602",
            manually_assigned_statement_id=None
        )

        snapshot = service.create_snapshot_from_installment(installment, None)

        assert snapshot.payment_method_name is None