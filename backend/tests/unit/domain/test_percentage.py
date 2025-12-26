# backend/tests/unit/domain/test_percentage.py
import pytest
from decimal import Decimal
from cashdata.domain.value_objects.percentage import Percentage
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.domain.exceptions.domain_exceptions import InvalidPercentage


class TestPercentageCreation:
    """Tests de creación de Percentage"""

    def test_should_create_percentage_with_valid_value(self):
        test_percentage = Percentage(Decimal("89"))

        assert test_percentage.value == Decimal("89")

    def test_should_create_percentage_with_zero(self):
        test_percentage = Percentage(Decimal("0"))

        assert test_percentage.value == Decimal("0")

    def test_should_create_percentage_with_hundred(self):
        test_percentage = Percentage(Decimal("100"))

        assert test_percentage.value == Decimal("100")

    def test_should_raise_exception_when_value_is_negative(self):
        with pytest.raises(InvalidPercentage) as err_desc:
            _ = Percentage(Decimal("-7"))

        assert "percentage must be between 0 and 100" in str(err_desc).lower()

    def test_should_raise_exception_when_value_exceeds_hundred(self):
        with pytest.raises(InvalidPercentage) as err_desc:
            _ = Percentage(Decimal("101"))

        assert "percentage must be between 0 and 100" in str(err_desc).lower()

    def test_should_normalize_int_to_decimal(self):
        test_percentage = Percentage(55)

        assert test_percentage.value == Decimal("55")

    def test_should_normalize_float_to_decimal(self):
        test_percentage = Percentage(16.578)

        assert test_percentage.value == Decimal("16.578")


class TestPercentageFromDecimal:
    """Tests del método from_decimal"""

    def test_should_create_percentage_from_valid_decimal(self):
        dec = Decimal("0.42")
        pct = Percentage.from_decimal(dec)

        assert pct.value == Decimal("42")

    def test_should_create_percentage_from_zero_decimal(self):
        dec = Decimal("0")
        pct = Percentage.from_decimal(dec)

        assert pct.value == Decimal("0")

    def test_should_create_percentage_from_one_decimal(self):
        dec = Decimal("1")
        pct = Percentage.from_decimal(dec)

        assert pct.value == Decimal("100")

    def test_should_raise_exception_when_decimal_is_negative(self):
        with pytest.raises(InvalidPercentage) as err_desc:
            _ = Percentage.from_decimal(Decimal("-0.71"))

        assert "decimal value must be between 0 and 1" in str(err_desc).lower()

    def test_should_raise_exception_when_decimal_exceeds_one(self):
        with pytest.raises(InvalidPercentage) as err_desc:
            _ = Percentage.from_decimal(Decimal("1.71"))

        assert "decimal value must be between 0 and 1" in str(err_desc).lower()


class TestPercentageToDecimal:
    """Tests del método to_decimal"""

    def test_should_convert_percentage_to_decimal(self):
        pct = Percentage(42).to_decimal()

        assert pct == Decimal("0.42")

    def test_should_convert_zero_percentage_to_zero_decimal(self):
        pct = Percentage(0).to_decimal()

        assert pct == Decimal("0")

    def test_should_convert_hundred_percentage_to_one_decimal(self):
        pct = Percentage(100).to_decimal()

        assert pct == Decimal("1")


class TestPercentageApplyTo:
    """Tests del método apply_to"""

    @pytest.mark.parametrize(
        "percentage,money_value,result",
        [
            (
                Percentage(Decimal("75")),
                Money(1000, Currency.ARS),
                Money(750, Currency.ARS),
            ),
            (
                Percentage(Decimal("75")),
                Money(1000, Currency.USD),
                Money(750, Currency.USD),
            )
        ],
        ids=["test_currency_ars", "test_currency_usd"]
    )
    def test_should_apply_percentage_to_money(self, percentage, money_value, result):
        assert percentage.apply_to(money_value) == result

    @pytest.mark.parametrize(
        "percentage,money_value,result",
        [
            (
                Percentage(Decimal("0")),
                Money(1000, Currency.ARS),
                Money(0, Currency.ARS),
            ),
            (
                Percentage(Decimal("0")),
                Money(1000, Currency.USD),
                Money(0, Currency.USD),
            )
        ],
        ids=["test_currency_ars", "test_currency_usd"]
    )
    def test_should_apply_zero_percentage_to_money(self, percentage, money_value, result):
        assert percentage.apply_to(money_value) == result

    @pytest.mark.parametrize(
        "percentage,money_value,result",
        [
            (
                Percentage(Decimal("100")),
                Money(1000, Currency.ARS),
                Money(1000, Currency.ARS),
            ),
            (
                Percentage(Decimal("100")),
                Money(1000, Currency.USD),
                Money(1000, Currency.USD),
            )
        ],
        ids=["test_currency_ars", "test_currency_usd"]
    )
    def test_should_apply_hundred_percentage_to_money(self, percentage, money_value, result):
        assert percentage.apply_to(money_value) == result


class TestPercentageAddition:
    """Tests de suma de porcentajes"""

    def test_should_add_two_percentages(self):
        pcts = [
            Percentage(Decimal("25")),
            Percentage(Decimal("25")),
        ]

        assert sum(pcts, Percentage(Decimal("0"))) == Percentage(Decimal("50"))

    def test_should_add_zero_percentage(self):
        pcts = [
            Percentage(Decimal("0")),
            Percentage(Decimal("0")),
        ]

        assert sum(pcts, Percentage(Decimal("0"))) == Percentage(Decimal("0"))

    def test_should_raise_exception_when_sum_exceeds_hundred(self):
        pcts = [
            Percentage(Decimal("90")),
            Percentage(Decimal("40")),
        ]

        with pytest.raises(InvalidPercentage) as err_desc:
            sum(pcts, Percentage(Decimal("0")))

        assert "sum of percentages cannot exceed" in str(err_desc).lower()

    def test_should_raise_exception_when_adding_non_percentage(self):
        pcts = [
            Percentage(Decimal("10")),
            Percentage(Decimal("10")),
            99.5
        ]

        with pytest.raises(InvalidPercentage) as err_desc:
            sum(pcts, Percentage(Decimal("0")))

        assert "cannot add percentage with" in str(err_desc).lower()

class TestPercentageSubtraction:
    """Tests de resta de porcentajes"""

    def test_should_subtract_two_percentages(self):
        pct1 = Percentage(Decimal("100"))
        pct2 = Percentage(Decimal("85"))

        assert pct1 - pct2 == Percentage(Decimal("15"))

    def test_should_subtract_zero_percentage(self):
        pct1 = Percentage(Decimal("100"))
        pct2 = Percentage(Decimal("0"))

        assert pct1 - pct2 == Percentage(Decimal("100"))

    def test_should_raise_exception_when_result_is_negative(self):
        pct1 = Percentage(Decimal("0"))
        pct2 = Percentage(Decimal("100"))

        with pytest.raises(InvalidPercentage) as err_desc:
            pct1 - pct2

        assert "result of subtraction cannot be negative" in str(err_desc).lower()

    def test_should_raise_exception_when_subtracting_non_percentage(self):
        pct = Percentage(Decimal("0"))

        with pytest.raises(InvalidPercentage) as err_desc:
            pct - 100

        assert "cannot subtract" in str(err_desc).lower()


class TestPercentageStringRepresentation:
    """Tests de representación en string"""

    def test_should_return_string_representation(self):
        pct = Percentage(Decimal("15.5"))

        assert str(pct) == "15.5%"

    def test_should_return_repr_representation(self):
        pct = Percentage(Decimal("15.5"))

        assert repr(pct) == "Percentage(15.5)"
