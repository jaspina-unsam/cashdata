import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from decimal import Decimal
from datetime import date

from app.domain.entities.purchase import Purchase
from app.domain.value_objects.money import Money, Currency
from app.infrastructure.persistence.models.purchase_model import PurchaseModel
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.models.credit_card_model import CreditCardModel
from app.infrastructure.persistence.models.category_model import CategoryModel
from app.infrastructure.persistence.repositories.sqlalchemy_purchase_repository import (
    SQLAlchemyPurchaseRepository,
)


@pytest.fixture
def db_session():
    """In-memory SQLite for tests"""
    engine = create_engine("sqlite:///:memory:")
    UserModel.metadata.create_all(engine)
    CategoryModel.metadata.create_all(engine)
    CreditCardModel.metadata.create_all(engine)
    PurchaseModel.metadata.create_all(engine)
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
    test_category = CategoryModel(id=1, name="Groceries")
    test_card = CreditCardModel(
        id=1,
        user_id=1,
        name="Visa",
        bank="HSBC",
        last_four_digits="1234",
        billing_close_day=10,
        payment_due_day=20,
    )
    session.add_all([test_user, test_category, test_card])
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
            credit_card_id=1,
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
            credit_card_id=1,
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
            credit_card_id=1,
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
            credit_card_id=1,
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
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="P1",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )
        p2 = Purchase(
            id=None,
            user_id=1,
            credit_card_id=1,
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


class TestSQLAlchemyPurchaseRepositoryFindByCreditCardId:
    def test_should_return_all_purchases_for_card(self, purchase_repository):
        p1 = Purchase(
            id=None,
            user_id=1,
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="P1",
            total_amount=Money(Decimal("1000.00"), Currency.ARS),
            installments_count=1,
        )
        purchase_repository.save(p1)

        purchases = purchase_repository.find_by_credit_card_id(1)
        assert len(purchases) >= 1
