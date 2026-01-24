import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from decimal import Decimal
from datetime import datetime, date

from app.domain.entities.purchase import Purchase

from app.infrastructure.persistence.models.purchase_model import PurchaseModel
from app.domain.value_objects.money import Money, Currency
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.models.category_model import CategoryModel
from app.infrastructure.persistence.models.credit_card_model import CreditCardModel
from app.infrastructure.persistence.models.installment_model import InstallmentModel
from app.infrastructure.persistence.models.payment_method_model import PaymentMethodModel
from app.infrastructure.persistence.repositories.sqlalchemy_purchase_repository import (
    SQLAlchemyPurchaseRepository,
)


@pytest.fixture
def db_session():
    """In-memory SQLite for tests"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    # Enable foreign keys for CASCADE deletes
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()

    UserModel.metadata.create_all(engine)
    CategoryModel.metadata.create_all(engine)
    PaymentMethodModel.metadata.create_all(engine)
    CreditCardModel.metadata.create_all(engine)
    PurchaseModel.metadata.create_all(engine)
    InstallmentModel.metadata.create_all(engine)  # Add installments table
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create test data
    test_user = UserModel(
        id=1,
        name="Test User",
        email="test@example.com",
        wage_amount=50000,
        wage_currency="ARS",
        is_deleted=False,
    )
    session.add(test_user)
    session.commit()

    test_category = CategoryModel(id=1, name="Groceries")
    session.add(test_category)
    session.commit()

    test_payment_method = PaymentMethodModel(
        id=1,
        user_id=1,
        type="credit_card",
        name="Test Card",
        is_active=True,
        created_at=datetime.now(),
    )
    session.add(test_payment_method)
    session.commit()

    test_card = CreditCardModel(
        id=1,
        payment_method_id=1,
        user_id=1,
        name="Visa",
        bank="HSBC",
        last_four_digits="1234",
        billing_close_day=10,
        payment_due_day=20,
    )
    session.add(test_card)
    session.commit()

    yield session
    session.close()


@pytest.fixture
def purchase_repository(db_session: Session):
    return SQLAlchemyPurchaseRepository(db_session)


class TestSQLAlchemyPurchaseRepositorySave:
    def test_should_save_new_purchase(self, purchase_repository):
        new_purchase = Purchase(
            id=None,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Supermarket shopping",
            total_amount=Money(Decimal("25000.00"), Currency.ARS),
            installments_count=1,
        )
        saved = purchase_repository.save(new_purchase)

        assert saved.id is not None
        assert saved.description == "Supermarket shopping"
        assert saved.total_amount.amount == Decimal("25000.00")

    def test_should_update_existing_purchase(self, purchase_repository):
        purchase = Purchase(
            id=None,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Electronics",
            total_amount=Money(Decimal("100000.00"), Currency.ARS),
            installments_count=12,
        )
        saved = purchase_repository.save(purchase)

        updated_purchase = Purchase(
            id=saved.id,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Electronics Updated",
            total_amount=Money(Decimal("120000.00"), Currency.ARS),
            installments_count=12,
        )
        updated = purchase_repository.save(updated_purchase)

        assert updated.id == saved.id
        assert updated.description == "Electronics Updated"


class TestSQLAlchemyPurchaseRepositoryFindById:
    def test_should_find_existing_purchase(self, purchase_repository):
        purchase = Purchase(
            id=None,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Test Purchase",
            total_amount=Money(Decimal("5000.00"), Currency.ARS),
            installments_count=1,
        )
        saved = purchase_repository.save(purchase)

        found = purchase_repository.find_by_id(saved.id)
        assert found is not None
        assert found.id == saved.id

    def test_should_return_none_for_nonexistent_id(self, purchase_repository):
        assert purchase_repository.find_by_id(999) is None


class TestSQLAlchemyPurchaseRepositoryFindByUserId:
    def test_should_return_all_purchases_for_user(self, purchase_repository):
        p1 = Purchase(
            id=None,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="P1",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )
        p2 = Purchase(
            id=None,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 16),
            description="P2",
            total_amount=Money(Decimal("2000.00"), Currency.ARS),
            installments_count=1,
        )

        purchase_repository.save(p1)
        purchase_repository.save(p2)

        purchases = purchase_repository.find_by_user_id(1)
        assert len(purchases) == 2


class TestSQLAlchemyPurchaseRepositoryFindByPaymentMethodId:
    def test_should_return_all_purchases_for_payment_method(self, purchase_repository):
        p1 = Purchase(
            id=None,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="P1",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )
        purchase_repository.save(p1)

        purchases = purchase_repository.find_by_payment_method_id(1)
        assert len(purchases) >= 1


class TestSQLAlchemyPurchaseRepositoryDelete:
    def test_should_delete_existing_purchase(self, purchase_repository):
        # Create a purchase
        purchase = Purchase(
            id=None,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Purchase to delete",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )
        saved_purchase = purchase_repository.save(purchase)
        purchase_id = saved_purchase.id

        # Verify it exists
        found = purchase_repository.find_by_id(purchase_id)
        assert found is not None

        # Delete it
        purchase_repository.delete(purchase_id)

        # Verify it's gone
        found_after_delete = purchase_repository.find_by_id(purchase_id)
        assert found_after_delete is None

    def test_should_delete_purchase_and_cascade_delete_installments(self, db_session):
        """Test that deleting a purchase also deletes its installments via CASCADE"""
        from app.infrastructure.persistence.repositories.sqlalchemy_installment_repository import (
            SQLAlchemyInstallmentRepository,
        )
        from app.domain.entities.installment import Installment
        from app.domain.value_objects.money import Money, Currency
        from decimal import Decimal

        # Create repositories
        purchase_repo = SQLAlchemyPurchaseRepository(db_session)
        installment_repo = SQLAlchemyInstallmentRepository(db_session)

        # Create a purchase
        purchase = Purchase(
            id=None,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Purchase with installments to delete",
            total_amount=Money(Decimal("3000.00"), Currency.ARS),
            installments_count=3,
        )
        saved_purchase = purchase_repo.save(purchase)
        purchase_id = saved_purchase.id

        # Create installments for this purchase
        installments = []
        for i in range(1, 4):
            installment = Installment(
                id=None,
                purchase_id=purchase_id,
                installment_number=i,
                total_installments=3,
                amount=Money(Decimal("1000.00"), Currency.ARS),
                billing_period="202501",
                manually_assigned_statement_id=None,
            )
            installments.append(installment)

        # Save installments
        for installment in installments:
            installment_repo.save(installment)

        # Verify purchase and installments exist
        found_purchase = purchase_repo.find_by_id(purchase_id)
        assert found_purchase is not None

        found_installments = db_session.query(InstallmentModel).filter_by(purchase_id=purchase_id).all()
        assert len(found_installments) == 3

        # Delete the purchase
        purchase_repo.delete(purchase_id)
        db_session.commit()  # Commit the transaction

        # Verify purchase is gone
        found_purchase_after = purchase_repo.find_by_id(purchase_id)
        assert found_purchase_after is None

        # Verify installments are also gone (CASCADE delete)
        found_installments_after = db_session.query(InstallmentModel).filter_by(purchase_id=purchase_id).all()
        assert len(found_installments_after) == 0

    def test_delete_purchase_also_deletes_budget_expense_responsibilities(self, db_session):
        """Deleting a purchase should remove related budget expenses and their responsibilities."""
        from app.infrastructure.persistence.models.budget_expense_model import BudgetExpenseModel
        from app.infrastructure.persistence.models.budget_expense_responsibility_model import BudgetExpenseResponsibilityModel
        from app.infrastructure.persistence.models.monthly_budget_model import MonthlyBudgetModel
        from app.infrastructure.persistence.repositories.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
        from app.application.use_cases.delete_purchase_use_case import DeletePurchaseUseCase
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime

        # Create a monthly budget required by BudgetExpenseModel
        budget = MonthlyBudgetModel(id=1, name="Test Budget", description=None, status="active", created_by_user_id=1, created_at=datetime.now())
        db_session.add(budget)
        db_session.commit()

        # Create a purchase
        from app.domain.entities.purchase import Purchase
        from app.domain.value_objects.money import Money, Currency
        from decimal import Decimal

        purchase_repo = SQLAlchemyPurchaseRepository(db_session)
        purchase = Purchase(
            id=None,
            user_id=1,
            payment_method_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Purchase with expense",
            total_amount=Money(Decimal("3000.00"), Currency.ARS),
            installments_count=1,
        )
        saved_purchase = purchase_repo.save(purchase)
        purchase_id = saved_purchase.id

        # Create a budget expense linked to the purchase
        expense = BudgetExpenseModel(
            budget_id=budget.id,
            purchase_id=purchase_id,
            installment_id=None,
            paid_by_user_id=1,
            split_type="full_single",
            amount=100.00,
            currency="ARS",
            description="Expense linked to purchase",
            date=date(2025, 1, 15),
            payment_method_name=None,
            created_at=datetime.now(),
        )
        db_session.add(expense)
        db_session.flush()

        # Add a responsibility for that expense
        responsibility = BudgetExpenseResponsibilityModel(
            budget_expense_id=expense.id,
            user_id=1,
            percentage=100.00,
            responsible_amount=100.00,
            responsible_currency="ARS",
        )
        db_session.add(responsibility)
        db_session.commit()

        # Verify entries exist
        found_expenses = db_session.query(BudgetExpenseModel).filter_by(purchase_id=purchase_id).all()
        assert len(found_expenses) == 1
        found_resps = db_session.query(BudgetExpenseResponsibilityModel).filter_by(budget_expense_id=expense.id).all()
        assert len(found_resps) == 1

        # Use DeletePurchaseUseCase to delete purchase
        # Create a unit of work that uses the same session
        uow = SQLAlchemyUnitOfWork(lambda: db_session)
        use_case = DeletePurchaseUseCase(uow)
        use_case.execute(purchase_id, 1)

        # After deletion, expense and responsibility should be gone
        found_expenses_after = db_session.query(BudgetExpenseModel).filter_by(purchase_id=purchase_id).all()
        assert len(found_expenses_after) == 0
        found_resps_after = db_session.query(BudgetExpenseResponsibilityModel).filter_by(budget_expense_id=expense.id).all()
        assert len(found_resps_after) == 0
