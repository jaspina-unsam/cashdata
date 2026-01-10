from decimal import Decimal
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.domain.entities.monthly_income import IncomeSource, MonthlyIncome
from app.domain.entities.user import User
from app.domain.entities.category import Category
from app.domain.entities.credit_card import CreditCard
from app.domain.entities.purchase import Purchase
from app.domain.entities.installment import Installment
from app.domain.value_objects.money import Currency, Money
from app.domain.value_objects.period import Period
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.models.monthly_income_model import (
    MonthlyIncomeModel,
)
from app.infrastructure.persistence.models.category_model import CategoryModel
from app.infrastructure.persistence.models.credit_card_model import CreditCardModel
from app.infrastructure.persistence.models.purchase_model import PurchaseModel
from app.infrastructure.persistence.models.installment_model import InstallmentModel
from app.infrastructure.persistence.repositories.sqlalchemy_unit_of_work import (
    SQLAlchemyUnitOfWork,
)


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite:///:memory:")
    UserModel.metadata.create_all(engine)
    MonthlyIncomeModel.metadata.create_all(engine)
    CategoryModel.metadata.create_all(engine)
    CreditCardModel.metadata.create_all(engine)
    PurchaseModel.metadata.create_all(engine)
    InstallmentModel.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine)

    yield SessionFactory


@pytest.fixture
def make_user():
    def _make(id, name, email, wage_amount, wage_currency=Currency.ARS):
        return User(
            id=id,
            name=name,
            email=email,
            wage=Money(Decimal(str(wage_amount)), wage_currency),
        )

    return _make


@pytest.fixture
def make_monthly_income():
    def _make(id, user_id, period, amount, source=IncomeSource.WAGE):
        return MonthlyIncome(
            id=id,
            user_id=user_id,
            period=period,
            amount=amount,
            source=source,
        )

    return _make


class TestSQLAlchemyUnitOfWork:

    def test_commit_persists_changes(self, session_factory, make_user, make_monthly_income):
        """
        GIVEN: Operaciones múltiples en UoW
        WHEN: Se hace commit
        THEN: Todos los cambios se persisten
        """
        user = make_user(1, "Olga", "olga@mail.com", 650000)
        user_olga_income1 = make_monthly_income(1, 1, Period.from_string("202507"), Money(Decimal("600000")))
        user_olga_income2 = make_monthly_income(2, 1, Period.from_string("202508"), Money(Decimal("650000")))
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            uow.users.save(user)
            uow.monthly_incomes.save(user_olga_income1)
            uow.monthly_incomes.save(user_olga_income2)
            uow.commit()

        with SQLAlchemyUnitOfWork(session_factory) as uow:
            saved_user = uow.users.find_by_id(1)
            incomes = uow.monthly_incomes.find_all_from_user(1)

        assert saved_user.name == "Olga"
        assert len(incomes) == 2
        assert sum([i.amount for i in incomes], Money(0)) == Money(1250000)

    def test_rollback_on_exception(self, session_factory, make_user):
        """
        GIVEN: Operación que lanza excepción
        WHEN: Sale del context manager
        THEN: Se hace rollback automático
        """
        user = make_user(1, "Olga", "olga@mail.com", 650000)
        with pytest.raises(TypeError) as err_desc:
            with SQLAlchemyUnitOfWork(session_factory) as uow:
                uow.users.save(user)
                raise TypeError("error here")

        with SQLAlchemyUnitOfWork(session_factory) as uow:
            saved_user = uow.users.find_by_id(1)

        assert "error here" in str(err_desc)
        assert saved_user is None

    def test_manual_rollback(self, session_factory, make_user, make_monthly_income):
        """
        GIVEN: Cambios en la session
        WHEN: Llamo explícitamente a uow.rollback()
        THEN: Los cambios no se persisten
        """
        user = make_user(1, "Olga", "olga@mail.com", 650000)
        user_olga_income1 = make_monthly_income(1, 1, Period.from_string("202507"), Money(Decimal("600000")))
        user_olga_income2 = make_monthly_income(2, 1, Period.from_string("202508"), Money(Decimal("650000")))
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            uow.users.save(user)
            uow.commit()
            uow.monthly_incomes.save(user_olga_income1)
            uow.monthly_incomes.save(user_olga_income2)
            uow.rollback()

        with SQLAlchemyUnitOfWork(session_factory) as uow:
            saved_user = uow.users.find_by_id(1)
            incomes = uow.monthly_incomes.find_all_from_user(1)

        assert saved_user.name == "Olga"
        assert len(incomes) == 0

    def test_repositories_share_same_session(self, session_factory, make_user, make_monthly_income):
        """
        GIVEN: Dos repositories en el mismo UoW
        WHEN: Uno hace flush
        THEN: El otro ve los cambios (misma session)
        """
        user = make_user(1, "Olga", "olga@mail.com", 650000)
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            uow.users.save(user)
            saved_user_name = uow.users.find_by_id(1).name

        with SQLAlchemyUnitOfWork(session_factory) as uow:
            saved_user = uow.users.find_by_id(1)

        assert saved_user_name == "Olga"
        assert saved_user is None

    def test_new_repositories_available(self, session_factory):
        """
        GIVEN: UnitOfWork inicializado
        WHEN: Se accede a los nuevos repositories
        THEN: Están disponibles y funcionan correctamente
        """
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            assert uow.categories is not None
            assert uow.credit_cards is not None
            assert uow.purchases is not None
            assert uow.installments is not None

    def test_commit_persists_purchase_with_all_dependencies(self, session_factory, make_user):
        """
        GIVEN: Purchase completa con todas sus dependencias
        WHEN: Se hace commit
        THEN: Todos los datos relacionados se persisten correctamente
        """
        user = make_user(1, "Juan", "juan@mail.com", 100000)
        category = Category(id=None, name="Electronics", color="#FF5733", icon="laptop")
        credit_card = CreditCard(
            id=None, user_id=1, name="Visa", bank="HSBC",
            last_four_digits="1234", billing_close_day=10,
            payment_due_day=20, credit_limit=None
        )
        
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            saved_user = uow.users.save(user)
            saved_category = uow.categories.save(category)
            saved_card = uow.credit_cards.save(credit_card)
            uow.commit()
            
            purchase = Purchase(
                id=None, user_id=saved_user.id, payment_method_id=saved_card.id,
                category_id=saved_category.id, purchase_date=date(2025, 1, 15),
                description="Laptop", total_amount=Money(Decimal("120000.00"), Currency.ARS),
                installments_count=12
            )
            saved_purchase = uow.purchases.save(purchase)
            uow.commit()

        with SQLAlchemyUnitOfWork(session_factory) as uow:
            retrieved_purchase = uow.purchases.find_by_id(saved_purchase.id)
            
        assert retrieved_purchase is not None
        assert retrieved_purchase.description == "Laptop"
        assert retrieved_purchase.total_amount.amount == Decimal("120000.00")
        assert retrieved_purchase.installments_count == 12

    def test_rollback_reverts_all_repositories_changes(self, session_factory, make_user):
        """
        GIVEN: Cambios en múltiples repositories
        WHEN: Se hace rollback
        THEN: Ningún cambio se persiste
        """
        user = make_user(1, "Ana", "ana@mail.com", 80000)
        category = Category(id=None, name="Food", color="#00FF00", icon="utensils")
        
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            uow.users.save(user)
            uow.categories.save(category)
            uow.rollback()

        with SQLAlchemyUnitOfWork(session_factory) as uow:
            saved_user = uow.users.find_by_id(1)
            all_categories = uow.categories.find_all()
            
        assert saved_user is None
        assert len(all_categories) == 0

    def test_all_repositories_share_same_session(self, session_factory, make_user):
        """
        GIVEN: Múltiples repositories en el mismo UoW
        WHEN: Se guardan entidades sin commit
        THEN: Todos comparten la misma sesión y ven los cambios
        """
        user = make_user(1, "Carlos", "carlos@mail.com", 90000)
        category = Category(id=None, name="Travel", color="#0000FF", icon="plane")
        
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            uow.users.save(user)
            uow.categories.save(category)
            # Sin commit, pero en la misma session deberían verse
            found_user = uow.users.find_by_id(1)
            all_categories = uow.categories.find_all()
            
            assert found_user is not None
            assert found_user.name == "Carlos"
            assert len(all_categories) == 1
            assert all_categories[0].name == "Travel"
