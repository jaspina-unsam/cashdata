import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from decimal import Decimal
from datetime import date

from cashdata.domain.entities.installment import Installment
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.infrastructure.persistence.models.installment_model import (
    InstallmentModel,
)
from cashdata.infrastructure.persistence.models.purchase_model import PurchaseModel
from cashdata.infrastructure.persistence.models.user_model import UserModel
from cashdata.infrastructure.persistence.models.credit_card_model import CreditCardModel
from cashdata.infrastructure.persistence.models.category_model import CategoryModel
from cashdata.infrastructure.persistence.repositories.sqlalchemy_installment_repository import (
    SQLAlchemyInstallmentRepository,
)


@pytest.fixture
def db_session():
    """In-memory SQLite for tests"""
    engine = create_engine("sqlite:///:memory:")
    UserModel.metadata.create_all(engine)
    CategoryModel.metadata.create_all(engine)
    CreditCardModel.metadata.create_all(engine)
    PurchaseModel.metadata.create_all(engine)
    InstallmentModel.metadata.create_all(engine)
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
    test_purchase = PurchaseModel(
        id=1,
        user_id=1,
        credit_card_id=1,
        category_id=1,
        purchase_date=date(2025, 1, 15),
        description="Test Purchase",
        total_amount=12000,
        total_currency="ARS",
        installments_count=6,
    )
    session.add_all([test_user, test_category, test_card, test_purchase])
    session.commit()

    yield session
    session.close()


@pytest.fixture
def installment_repository(db_session: Session):
    return SQLAlchemyInstallmentRepository(db_session)


class TestSQLAlchemyInstallmentRepositorySave:
    def test_should_save_new_installment(self, installment_repository):
        installment = Installment(
            id=None,
            purchase_id=1,
            installment_number=1,
            total_installments=6,
            amount=Money(Decimal("2000.00"), Currency.ARS),
            billing_period="202501",
            due_date=date(2025, 2, 10),
        )
        saved = installment_repository.save(installment)

        assert saved.id is not None
        assert saved.installment_number == 1
        assert saved.amount.amount == Decimal("2000.00")

    def test_should_save_all_installments(self, installment_repository):
        installments = [
            Installment(
                id=None,
                purchase_id=1,
                installment_number=i,
                total_installments=3,
                amount=Money(Decimal("1000.00"), Currency.ARS),
                billing_period=f"20250{i}",
                due_date=date(2025, i, 10),
            )
            for i in range(1, 4)
        ]
        saved_list = installment_repository.save_all(installments)
        assert len(saved_list) == 3
        assert all(i.id is not None for i in saved_list)


class TestSQLAlchemyInstallmentRepositoryFindByPurchaseId:
    def test_should_return_all_installments_for_purchase(self, installment_repository):
        for i in range(1, 4):
            inst = Installment(
                id=None,
                purchase_id=1,
                installment_number=i,
                total_installments=3,
                amount=Money(Decimal("1000.00"), Currency.ARS),
                billing_period=f"20250{i}",
                due_date=date(2025, i, 10),
            )
            installment_repository.save(inst)

        installments = installment_repository.find_by_purchase_id(1)
        assert len(installments) == 3


class TestSQLAlchemyInstallmentRepositoryFindByBillingPeriod:
    def test_should_return_installments_for_period(self, installment_repository):
        inst = Installment(
            id=None,
            purchase_id=1,
            installment_number=1,
            total_installments=1,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202501",
            due_date=date(2025, 2, 10),
        )
        installment_repository.save(inst)

        installments = installment_repository.find_by_billing_period("202501")
        assert len(installments) >= 1


class TestSQLAlchemyInstallmentRepositoryFindByCreditCardAndPeriod:
    def test_should_return_installments_for_card_and_period(
        self, installment_repository
    ):
        inst = Installment(
            id=None,
            purchase_id=1,
            installment_number=1,
            total_installments=1,
            amount=Money(Decimal("5000.00"), Currency.ARS),
            billing_period="202501",
            due_date=date(2025, 2, 10),
        )
        installment_repository.save(inst)

        installments = installment_repository.find_by_credit_card_and_period(
            1, "202501"
        )
        assert len(installments) >= 1
