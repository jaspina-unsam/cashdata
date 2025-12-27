from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from cashdata.domain.entities.monthly_income import IncomeSource, MonthlyIncome
from cashdata.domain.entities.user import User
from cashdata.domain.value_objects.money import Currency, Money
from cashdata.domain.value_objects.period import Period
from cashdata.infrastructure.persistence.models.user_model import UserModel
from cashdata.infrastructure.persistence.models.monthly_income_model import (
    MonthlyIncomeModel,
)
from cashdata.infrastructure.persistence.repositories.sqlalchemy_unit_of_work import (
    SQLAlchemyUnitOfWork,
)


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite:///:memory:")
    UserModel.metadata.create_all(engine)
    MonthlyIncomeModel.metadata.create_all(engine)
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
