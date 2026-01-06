# backend/tests/unit/domain/test_monthly_income.py
import pytest
from decimal import Decimal
from app.domain.entities.monthly_income import MonthlyIncome, IncomeSource
from app.domain.value_objects.money import Money, Currency
from app.domain.value_objects.period import Period


@pytest.fixture
def period_october_25():
    return Period.from_string("202510")


@pytest.fixture
def default_amount():
    return Money(Decimal("1000"))


class TestMonthlyIncomeCreation:
    """Tests de creación de MonthlyIncome"""

    def test_should_create_monthly_income_with_all_fields(
        self, period_october_25, default_amount
    ):
        mi = MonthlyIncome(
            1, 1, period_october_25, default_amount, IncomeSource.FREELANCE
        )

        assert mi.id == 1
        assert mi.user_id == 1
        assert mi.period == period_october_25
        assert mi.amount == default_amount
        assert mi.source == IncomeSource.FREELANCE

    def test_should_create_monthly_income_with_default_source(
        self, period_october_25, default_amount
    ):
        mi = MonthlyIncome(1, 1, period_october_25, default_amount)

        assert mi.id == 1
        assert mi.user_id == 1
        assert mi.period == period_october_25
        assert mi.amount == default_amount
        assert mi.source == IncomeSource.WAGE

    def test_should_create_monthly_income_with_different_sources(
        self, period_october_25, default_amount
    ):
        mi = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.OTHER)

        assert mi.id == 1
        assert mi.user_id == 1
        assert mi.period == period_october_25
        assert mi.amount == default_amount
        assert mi.source == IncomeSource.OTHER


class TestMonthlyIncomeEquality:
    """Tests de igualdad y hash de MonthlyIncome"""

    def test_should_be_equal_when_ids_are_same(self, period_october_25, default_amount):
        mi1 = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.OTHER)
        mi2 = MonthlyIncome(
            1, 2, period_october_25, default_amount * 2, IncomeSource.WAGE
        )

        assert mi1 == mi2

    def test_should_not_be_equal_when_ids_are_different(
        sel, period_october_25, default_amount
    ):
        mi1 = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.OTHER)
        mi2 = MonthlyIncome(
            2, 2, period_october_25, default_amount * 2, IncomeSource.WAGE
        )

        assert mi1 != mi2

    def test_should_not_be_equal_when_comparing_with_non_monthly_income(
        self, period_october_25, default_amount
    ):
        mi1 = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.OTHER)
        mi2 = default_amount

        assert mi1 != mi2

    def test_should_have_same_hash_when_ids_are_same(
        self, period_october_25, default_amount
    ):
        mi1 = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.OTHER)
        mi2 = MonthlyIncome(
            1, 2, period_october_25, default_amount * 2, IncomeSource.WAGE
        )

        assert hash(mi1) == hash(mi2)

    def test_should_have_different_hash_when_ids_are_different(
        self, period_october_25, default_amount
    ):
        mi1 = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.OTHER)
        mi2 = MonthlyIncome(
            2, 2, period_october_25, default_amount * 2, IncomeSource.WAGE
        )

        assert hash(mi1) != hash(mi2)


class TestMonthlyIncomeUpdateAmount:
    """Tests del método update_amount"""

    def test_should_update_amount_with_valid_money(
        self, period_october_25, default_amount
    ):
        mi = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.WAGE)

        new_amount = Money(Decimal("1000000"))
        mi.update_amount(new_amount)

        assert mi.amount == new_amount

    def test_should_raise_exception_when_updating_with_invalid_type(self, period_october_25, default_amount):
        mi = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.WAGE)

        new_amount = 1_000

        with pytest.raises(TypeError) as err_desc:
            mi.update_amount(new_amount)

        assert "cannot set" in str(err_desc).lower()


class TestMonthlyIncomeUpdateSource:
    """Tests del método update_source"""

    def test_should_update_source_with_valid_income_source(self, period_october_25, default_amount):
        mi = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.WAGE)

        new_source = IncomeSource.FREELANCE
        mi.update_source(new_source)

        assert mi.source == new_source

    def test_should_raise_exception_when_updating_with_invalid_type(self, period_october_25, default_amount):
        mi = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.WAGE)

        new_source = "WAGE"

        with pytest.raises(TypeError) as err_desc:
            mi.update_source(new_source)

        assert "cannot set" in str(err_desc).lower()


class TestMonthlyIncomeUpdatePeriod:
    """Tests del método update_period"""

    def test_should_update_period_with_valid_period(self, period_october_25, default_amount):
        mi = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.WAGE)

        new_period = Period.from_string("202512")
        mi.update_period(new_period)

        assert mi.period == new_period

    def test_should_raise_exception_when_updating_with_invalid_type(self, period_october_25, default_amount):
        mi = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.WAGE)

        new_period = "202512"

        with pytest.raises(TypeError) as err_desc:
            mi.update_period(new_period)

        assert "cannot set" in str(err_desc).lower()


class TestMonthlyIncomeStringRepresentation:
    """Tests de representación en string"""

    def test_should_return_string_representation(self, period_october_25, default_amount):
        mi = MonthlyIncome(1, 1, period_october_25, default_amount, IncomeSource.WAGE)

        assert str(mi) == f"MonthlyIncome({period_october_25}, {default_amount}, {IncomeSource.WAGE})"
