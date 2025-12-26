import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from cashdata.domain.entities.monthly_income import MonthlyIncome, IncomeSource
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.domain.value_objects.period import Period
from cashdata.infrastructure.persistence.models.monthly_income_model import (
    MonthlyIncomeModel,
)
from cashdata.infrastructure.persistence.repositories.sqlalchemy_monthly_income_repository import (
    SQLAlchemyMonthlyIncomeRepository,
)
from decimal import Decimal


@pytest.fixture
def db_session():
    """In-memory SQLite for tests"""
    engine = create_engine("sqlite:///:memory:")
    MonthlyIncomeModel.metadata.create_all(engine)  # Create tables
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


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


@pytest.fixture
def monthly_income_repository(db_session: Session):
    return SQLAlchemyMonthlyIncomeRepository(db_session)


class TestSQLAlchemyMonthlyIncomeRepositorySave:
    def test_should_save_new_monthly_income(
        self, monthly_income_repository, make_monthly_income
    ):
        # Arrange
        period = Period(2025, 12)
        amount = Money(Decimal("50000"), Currency.ARS)
        new_income = make_monthly_income(None, 1, period, amount)

        # Act
        saved_income = monthly_income_repository.save(new_income)

        # Assert
        assert saved_income.id is not None
        assert saved_income.user_id == 1
        assert saved_income.period == period
        assert saved_income.amount.amount == Decimal("50000")
        assert saved_income.amount.currency == Currency.ARS
        assert saved_income.source == IncomeSource.WAGE

        # Verify in DB
        retrieved = monthly_income_repository.find_by_id(saved_income.id)
        assert retrieved == saved_income

    def test_should_update_existing_monthly_income(
        self, monthly_income_repository, make_monthly_income
    ):
        """
        Given: A monthly income exists in DB
        When: I modify the income and save again
        Then: The changes should persist
        """
        # 1. Crear y guardar
        period = Period(2025, 12)
        income = make_monthly_income(
            None, 1, period, Money(Decimal("5000"), Currency.ARS)
        )
        saved = monthly_income_repository.save(income)
        original_id = saved.id

        # 2. Modificar y guardar de nuevo
        saved.update_amount(Money(Decimal("6000"), Currency.ARS))
        updated = monthly_income_repository.save(saved)

        # 3. Verificar que se actualizó (mismo ID)
        assert updated.id == original_id
        assert updated.amount.amount == Decimal("6000")

        # 4. Verificar en DB
        from_db = monthly_income_repository.find_by_id(original_id)
        assert from_db.amount.amount == Decimal("6000")

    def test_should_save_monthly_income_with_different_currency_and_source(
        self, monthly_income_repository, make_monthly_income
    ):
        """
        Given: A monthly income with USD and FREELANCE source
        When: I save the income
        Then: Currency and source should be preserved
        """
        period = Period(2025, 11)
        amount = Money(Decimal("3000"), Currency.USD)
        income = make_monthly_income(None, 2, period, amount, IncomeSource.FREELANCE)
        saved = monthly_income_repository.save(income)

        retrieved = monthly_income_repository.find_by_id(saved.id)
        assert retrieved.amount.currency == Currency.USD
        assert retrieved.source == IncomeSource.FREELANCE

    def test_should_handle_duplicate_user_period(
        self, monthly_income_repository, make_monthly_income
    ):
        """
        Given: A monthly income for user 1, period 202512 exists
        When: I try to save another income for same user and period
        Then: Should raise an exception (unique constraint)
        """
        period = Period(2025, 12)
        income1 = make_monthly_income(
            None, 1, period, Money(Decimal("5000"), Currency.ARS)
        )
        monthly_income_repository.save(income1)

        income2 = make_monthly_income(
            None, 1, period, Money(Decimal("6000"), Currency.ARS)
        )

        with pytest.raises(Exception):  # SQLAlchemy raises IntegrityError
            monthly_income_repository.save(income2)
            monthly_income_repository.session.commit()  # Force constraint check


class TestSQLAlchemyMonthlyIncomeRepositoryFind:
    def test_should_find_monthly_income_by_id(
        self, monthly_income_repository, make_monthly_income
    ):
        """
        Given: A monthly income exists in DB
        When: I search by ID
        Then: Should return the correct income
        """
        period = Period(2025, 12)
        income = make_monthly_income(
            None, 1, period, Money(Decimal("5000"), Currency.ARS)
        )
        saved = monthly_income_repository.save(income)

        found = monthly_income_repository.find_by_id(saved.id)

        assert found is not None
        assert found.id == saved.id
        assert found.user_id == 1
        assert found.period == period

    def test_should_return_none_when_monthly_income_not_found(
        self, monthly_income_repository
    ):
        """
        Given: No incomes in DB
        When: I search for ID 999
        Then: Should return None
        """
        result = monthly_income_repository.find_by_id(999)
        assert result is None

    def test_should_find_all_monthly_incomes(
        self, monthly_income_repository, make_monthly_income
    ):
        """
        Given: Multiple incomes in DB
        When: I call find_all()
        Then: Should return all incomes
        """
        period1 = Period(2025, 12)
        period2 = Period(2025, 11)
        income1 = make_monthly_income(
            None, 1, period1, Money(Decimal("5000"), Currency.ARS)
        )
        income2 = make_monthly_income(
            None, 2, period2, Money(Decimal("6000"), Currency.USD)
        )
        income3 = make_monthly_income(
            None, 1, period2, Money(Decimal("7000"), Currency.ARS)
        )

        monthly_income_repository.save(income1)
        monthly_income_repository.save(income2)
        monthly_income_repository.save(income3)

        all_incomes = monthly_income_repository.find_all()

        assert len(all_incomes) == 3
        assert all(isinstance(i, MonthlyIncome) for i in all_incomes)

    def test_should_return_empty_list_when_no_incomes(self, monthly_income_repository):
        """
        Given: No incomes in DB
        When: I call find_all()
        Then: Should return empty list
        """
        result = monthly_income_repository.find_all()
        assert result == []

    def test_should_find_all_incomes_from_user(
        self, monthly_income_repository, make_monthly_income
    ):
        """
        Given: Multiple incomes for different users
        When: I call find_all_from_user(1)
        Then: Should return only incomes from user 1
        """
        period1 = Period(2025, 12)
        period2 = Period(2025, 11)
        income1 = make_monthly_income(
            None, 1, period1, Money(Decimal("5000"), Currency.ARS)
        )
        income2 = make_monthly_income(
            None, 2, period2, Money(Decimal("6000"), Currency.USD)
        )
        income3 = make_monthly_income(
            None, 1, period2, Money(Decimal("7000"), Currency.ARS)
        )

        monthly_income_repository.save(income1)
        monthly_income_repository.save(income2)
        monthly_income_repository.save(income3)

        user_incomes = monthly_income_repository.find_all_from_user(1)

        assert len(user_incomes) == 2
        assert all(i.user_id == 1 for i in user_incomes)

    def test_should_return_empty_list_when_no_incomes_from_user(
        self, monthly_income_repository
    ):
        """
        Given: No incomes for user 999
        When: I call find_all_from_user(999)
        Then: Should return empty list
        """
        result = monthly_income_repository.find_all_from_user(999)
        assert result == []


class TestSQLAlchemyMonthlyIncomeRepositoryDelete:
    def test_should_delete_existing_monthly_income(
        self, monthly_income_repository, make_monthly_income
    ):
        """
        Given: A monthly income exists in DB
        When: I delete the income
        Then: The income should no longer exist
        """
        period = Period(2025, 12)
        income = make_monthly_income(
            None, 1, period, Money(Decimal("5000"), Currency.ARS)
        )
        saved = monthly_income_repository.save(income)
        income_id = saved.id

        # Delete
        result = monthly_income_repository.delete(income_id)

        assert result is True

        # Verify deleted
        found = monthly_income_repository.find_by_id(income_id)
        assert found is None

    def test_should_return_false_when_deleting_nonexistent_monthly_income(
        self, monthly_income_repository
    ):
        """
        Given: No income with ID 999
        When: I try to delete ID 999
        Then: Should return False
        """
        result = monthly_income_repository.delete(999)
        assert result is False


class TestFindByPeriod:
    def test_should_find_all_incomes_for_period(self, monthly_income_repository, make_monthly_income):
        """
        Given: 3 users with incomes in Dec 2025, 2 users in Nov 2025
        When: I search for Dec 2025
        Then: Should return only the 3 from Dec
        """
        period_dec = Period(2025, 12)
        period_nov = Period(2025, 11)

        # Dec incomes
        monthly_income_repository.save(make_monthly_income(None, 1, period_dec, Money(Decimal("2540"), Currency.USD)))
        monthly_income_repository.save(make_monthly_income(None, 2, period_dec, Money(Decimal("1800"), Currency.USD)))
        monthly_income_repository.save(make_monthly_income(None, 3, period_dec, Money(Decimal("3000"), Currency.USD)))

        # Nov incomes
        monthly_income_repository.save(make_monthly_income(None, 1, period_nov, Money(Decimal("2500"), Currency.USD)))
        monthly_income_repository.save(make_monthly_income(None, 2, period_nov, Money(Decimal("1700"), Currency.USD)))

        # Act
        result = monthly_income_repository.find_by_period(period_dec)

        # Assert
        assert len(result) == 3
        assert all(inc.period == period_dec for inc in result)


class TestFindByUserAndPeriod:
    def test_should_find_specific_user_income_for_period(
        self, monthly_income_repository, make_monthly_income
    ):
        """
        Given: User 1 has incomes in multiple periods
        When: I search for user 1 in Dec 2025
        Then: Should return only that specific income
        """
        period_dec = Period(2025, 12)
        period_nov = Period(2025, 11)

        monthly_income_repository.save(make_monthly_income(None, 1, period_dec, Money(Decimal("2540"), Currency.USD)))
        monthly_income_repository.save(make_monthly_income(None, 1, period_nov, Money(Decimal("2500"), Currency.USD)))
        monthly_income_repository.save(make_monthly_income(None, 2, period_dec, Money(Decimal("1800"), Currency.USD)))

        # Act
        result = monthly_income_repository.find_by_user_and_period(1, period_dec)

        # Assert
        assert result is not None
        assert result.user_id == 1
        assert result.period == period_dec
        assert result.amount.amount == Decimal("2540")

    def test_should_return_none_when_no_income_for_user_period(self, monthly_income_repository):
        """
        Given: No incomes exist
        When: I search for user 999 in any period
        Then: Should return None
        """
        result = monthly_income_repository.find_by_user_and_period(999, Period(2025, 12))
        assert result is None
