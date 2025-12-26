# backend/tests/unit/domain/test_period.py
import pytest
from datetime import date
from cashdata.domain.value_objects.period import Period
from cashdata.domain.exceptions.domain_exceptions import InvalidPeriodFormat


class TestPeriodCreation:
    """Tests de creación de Period"""

    def test_should_create_period_with_valid_year_and_month(self):
        test_period = Period(2025, 10)

        assert test_period.year == 2025
        assert test_period.month == 10

    def test_should_create_period_with_minimum_year(self):
        test_period = Period(2001, 10)

        assert test_period.year == 2001
        assert test_period.month == 10

    def test_should_raise_exception_when_month_is_less_than_one(self):
        with pytest.raises(InvalidPeriodFormat) as err_desc:
            _ = Period(2005, 0)

        assert "month must be between" in str(err_desc).lower()

    def test_should_raise_exception_when_month_exceeds_twelve(self):
        with pytest.raises(InvalidPeriodFormat) as err_desc:
            _ = Period(2005, 25)

        assert "month must be between" in str(err_desc).lower()

    def test_should_raise_exception_when_year_is_less_than_two_thousand(self):
        with pytest.raises(InvalidPeriodFormat) as err_desc:
            _ = Period(1989, 10)

        assert "year must be" in str(err_desc).lower()


class TestPeriodFromString:
    """Tests del método from_string"""

    def test_should_create_period_from_valid_string(self):
        test_period = Period.from_string("202510")

        assert test_period.year == 2025
        assert test_period.month == 10

    def test_should_raise_exception_when_string_is_too_short(self):
        with pytest.raises(InvalidPeriodFormat) as err_desc:
            _ = Period.from_string("2512")

        assert "period string must be yyyymm format" in str(err_desc).lower()

    def test_should_raise_exception_when_string_is_too_long(self):
        with pytest.raises(InvalidPeriodFormat) as err_desc:
            _ = Period.from_string("20251201")

        assert "period string must be yyyymm format" in str(err_desc).lower()

    def test_should_raise_exception_when_string_contains_non_digits(self):
        with pytest.raises(InvalidPeriodFormat) as err_desc:
            _ = Period.from_string("veinteveinticincodoce")

        assert "period string must be yyyymm format" in str(err_desc).lower()


class TestPeriodFromDate:
    """Tests del método from_date"""

    def test_should_create_period_from_date(self):
        test_period = Period.from_date(date(2025, 10, 3))

        assert test_period.year == 2025
        assert test_period.month == 10


class TestPeriodCurrent:
    """Tests del método current"""

    def test_should_return_current_period(self):
        test_period = Period.current()

        assert test_period.year == date.today().year
        assert test_period.month == date.today().month


class TestPeriodToString:
    """Tests del método to_string"""

    def test_should_convert_period_to_string(self):
        test_period = Period.from_string("202510")

        assert test_period.to_string() == "202510"

    def test_should_format_month_with_leading_zero(self):
        test_period = Period.from_string("202505")

        assert test_period.to_string() == "202505"


class TestPeriodNavigation:
    """Tests de navegación de periodos"""

    def test_should_return_next_period(self):
        test_period = Period.from_string("202505").next()

        assert test_period.year == 2025
        assert test_period.month == 6


    def test_should_return_next_period_at_year_end(self):
        test_period = Period.from_string("202412").next()

        assert test_period.year == 2025
        assert test_period.month == 1

    def test_should_return_previous_period(self):
        test_period = Period.from_string("202507").previous()

        assert test_period.year == 2025
        assert test_period.month == 6

    def test_should_return_previous_period_at_year_start(self):
        test_period = Period.from_string("202501").previous()

        assert test_period.year == 2024
        assert test_period.month == 12

    def test_should_add_positive_months(self):
        test_period = Period.from_string("202501").add_months(12)

        assert test_period.year == 2026
        assert test_period.month == 1

    def test_should_add_negative_months(self):
        test_period = Period.from_string("202501").add_months(-1)

        assert test_period.year == 2024
        assert test_period.month == 12

    def test_should_add_zero_months(self):
        test_period = Period.from_string("202412").add_months(0)

        assert test_period.year == 2024
        assert test_period.month == 12


class TestPeriodStringRepresentation:
    """Tests de representación en string"""

    def test_should_return_string_representation(self):
        test_period = Period.from_string("202501")

        assert str(test_period) == "202501"