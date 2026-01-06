# backend/tests/unit/domain/test_money.py
import pytest
from decimal import Decimal
from app.domain.value_objects.money import Currency, Money
from app.domain.exceptions.domain_exceptions import InvalidMoneyOperation


class TestMoneyCreation:
    """Tests de creación de Money"""

    @pytest.mark.parametrize(
        "amount,currency",
        [
            (Decimal("100"), Currency.ARS),
            (Decimal("50.5"), Currency.USD),
        ],
    )
    def test_should_create_money_with_valid_amount_and_currency(self, amount, currency):
        money = Money(amount, currency)

        assert money.amount == amount
        assert money.currency == currency

    @pytest.mark.parametrize(
        "amount,currency",
        [
            (Decimal("0"), Currency.ARS),
            (Decimal("0"), Currency.USD),
        ],
    )
    def test_should_create_money_when_amount_is_zero(self, amount, currency):
        money = Money(amount, currency)

        assert money.amount == amount
        assert money.currency == currency

    @pytest.mark.parametrize(
        "amount,currency",
        [
            (Decimal("-10.67"), Currency.ARS),
            (Decimal("-500.5"), Currency.USD),
        ],
    )
    def test_should_create_money_when_amount_is_negative(self, amount, currency):
        money = Money(amount, currency)

        assert money.amount == amount
        assert money.currency == currency

    @pytest.mark.parametrize(
        "amount,currency,result",
        [
            ("1", Currency.ARS, Decimal("1")),
            (15, Currency.USD, Decimal("15")),
            (3.5, Currency.USD, Decimal("3.5")),
        ],
    )
    def test_should_create_money_when_amount_is_parsed_as_decimal(
        self, amount, currency, result
    ):
        money = Money(amount, currency)

        assert money.amount == result

    def test_should_create_money_with_implicit_currency_is_ars(self):
        money = Money(15)

        assert money.amount == Decimal("15")
        assert money.currency == Currency.ARS

    def test_should_raise_exception_when_type_for_amount_is_incorrect(self):
        bad_amount = ["this", "will", "not", "work"]
        currency = Currency.ARS

        with pytest.raises(InvalidMoneyOperation) as exc_info:
            _ = Money(bad_amount, currency)

        assert "invalid type for decimal" in str(exc_info.value).lower()


class TestMoneyAddition:
    """Tests de suma"""

    @pytest.mark.parametrize(
        "money1,money2, result",
        [
            (
                Money(Decimal("100"), Currency.ARS),
                Money(Decimal("100"), Currency.ARS),
                Money(Decimal("200"), Currency.ARS),
            ),
            (
                Money(Decimal("-100"), Currency.ARS),
                Money(Decimal("100"), Currency.ARS),
                Money(Decimal("0"), Currency.ARS),
            ),
            (
                Money(Decimal("-100"), Currency.ARS),
                Money(Decimal("-100"), Currency.ARS),
                Money(Decimal("-200"), Currency.ARS),
            ),
            (
                Money(Decimal("100"), Currency.USD),
                Money(Decimal("100"), Currency.USD),
                Money(Decimal("200"), Currency.USD),
            ),
        ],
    )
    def test_should_add_money_when_currency_matches(self, money1, money2, result):
        assert (money1 + money2).amount == result.amount
        assert (money1 + money2).currency == result.currency

    def test_should_raise_exception_when_adding_different_currencies(self):
        money_ars = Money(Decimal("100"), Currency.ARS)
        money_usd = Money(Decimal("50"), Currency.USD)

        with pytest.raises(InvalidMoneyOperation) as exc_info:
            _ = money_ars + money_usd

        assert "currency mismatch: cannot add " in str(exc_info.value).lower()

    def test_should_raise_exception_when_adding_non_money_object(self):
        money_ars = Money(Decimal("100"), Currency.ARS)
        non_money = "200 ARS"

        with pytest.raises(InvalidMoneyOperation) as exc_info:
            _ = money_ars + non_money

        assert "invalid operation between" in str(exc_info.value).lower()


class TestMoneySubtraction:
    """Tests de resta"""

    @pytest.mark.parametrize(
        "money1,money2, result",
        [
            (
                Money(Decimal("300"), Currency.ARS),
                Money(Decimal("100"), Currency.ARS),
                Money(Decimal("200"), Currency.ARS),
            ),
            (
                Money(Decimal("-100"), Currency.ARS),
                Money(Decimal("100"), Currency.ARS),
                Money(Decimal("-200"), Currency.ARS),
            ),
            (
                Money(Decimal("-100"), Currency.ARS),
                Money(Decimal("-100"), Currency.ARS),
                Money(Decimal("0"), Currency.ARS),
            ),
            (
                Money(Decimal("100"), Currency.USD),
                Money(Decimal("50"), Currency.USD),
                Money(Decimal("50"), Currency.USD),
            ),
        ],
    )
    def test_should_substract_money_when_currency_matches(self, money1, money2, result):
        assert (money1 - money2).amount == result.amount
        assert (money1 - money2).currency == result.currency

    def test_should_raise_exception_when_substracting_different_currencies(self):
        money_ars = Money(Decimal("100"), Currency.ARS)
        money_usd = Money(Decimal("50"), Currency.USD)

        with pytest.raises(InvalidMoneyOperation) as exc_info:
            _ = money_ars - money_usd

        assert "currency mismatch: cannot subtract" in str(exc_info.value).lower()

    def test_should_raise_exception_when_substracting_non_money_object(self):
        money_ars = Money(Decimal("100"), Currency.ARS)
        non_money = "200 ARS"

        with pytest.raises(InvalidMoneyOperation) as exc_info:
            _ = money_ars - non_money

        assert "invalid operation between" in str(exc_info.value).lower()


class TestMoneyMultiplication:
    """Tests de multiplicación"""

    @pytest.mark.parametrize(
        "money1,factor,result",
        [
            (
                Money(Decimal("100"), Currency.ARS),
                2,
                Money(Decimal("200"), Currency.ARS),
            ),
            (
                Money(Decimal("100"), Currency.ARS),
                -1.5,
                Money(Decimal("-150"), Currency.ARS),
            ),
        ],
    )
    def test_should_multiply_money_with_int(self, money1, factor, result):
        assert (money1 * factor).amount == result.amount
        assert (money1 * factor).currency == result.currency

    def test_should_multiply_money_with_decimal(self):
        money = Money(100)
        factor = Decimal(10)

        assert (money * factor).amount == Decimal("1000")

    def test_should_raise_exception_when_multiplying_with_invalid_type(self):
        money = Money(Decimal("100"), Currency.ARS)
        invalid_factor = "2"

        with pytest.raises(InvalidMoneyOperation) as exc_info:
            _ = money * invalid_factor

        assert "money can only be multiplied by numbers" in str(exc_info.value).lower()


class TestMoneyDivision:
    """Tests de división"""

    def test_should_divide_money_by_integer(self):
        money = Money(Decimal("100"), Currency.ARS)
        divisor = 2

        result = money / divisor

        assert result.amount == Decimal("50")
        assert result.currency == Currency.ARS

    def test_should_divide_money_by_decimal(self):
        money = Money(Decimal("100"), Currency.ARS)
        divisor = Decimal("4")

        result = money / divisor

        assert result.amount == Decimal("25")
        assert result.currency == Currency.ARS

    def test_should_handle_division_with_remainder(self):
        money = Money(Decimal("100"), Currency.ARS)
        divisor = 3

        result = money / divisor

        assert result.amount == Decimal("100") / 3
        assert result.currency == Currency.ARS

    def test_should_raise_when_dividing_by_zero(self):
        money = Money(Decimal("100"), Currency.ARS)

        with pytest.raises(ZeroDivisionError):
            _ = money / 0


class TestMoneyComparison:
    """Tests de comparación"""

    def test_should_compare_equal_money(self):
        money1 = Money(Decimal("100"), Currency.ARS)
        money2 = Money(Decimal("100"), Currency.ARS)

        assert money1 == money2

    def test_should_compare_not_equal_money(self):
        money1 = Money(Decimal("100"), Currency.ARS)
        money2 = Money(Decimal("50"), Currency.ARS)

        assert money1 != money2

    def test_should_raise_when_comparing_different_currencies(self):
        money_ars = Money(Decimal("100"), Currency.ARS)
        money_usd = Money(Decimal("100"), Currency.USD)

        with pytest.raises(InvalidMoneyOperation):
            _ = money_ars < money_usd

    def test_should_return_false_when_comparing_with_non_money_object(self):
        money = Money(Decimal("100"), Currency.ARS)
        non_money = "100 ARS"

        assert (money != non_money) == True

    def test_less_than(self):
        money1 = Money(Decimal("50"), Currency.ARS)
        money2 = Money(Decimal("100"), Currency.ARS)

        assert money1 < money2

    def test_greater_than(self):
        money1 = Money(Decimal("150"), Currency.ARS)
        money2 = Money(Decimal("100"), Currency.ARS)

        assert money1 > money2

    def test_less_equal(self):
        money1 = Money(Decimal("100"), Currency.ARS)
        money2 = Money(Decimal("100"), Currency.ARS)

        assert money1 <= money2

    def test_greater_equal(self):
        money1 = Money(Decimal("100"), Currency.ARS)
        money2 = Money(Decimal("100"), Currency.ARS)

        assert money1 >= money2


class TestMoneyConversion:
    """Tests de conversión de moneda"""

    def test_convert_to_same_currency_returns_self(self):
        money = Money(Decimal("10"), Currency.ARS)

        assert money.convert_to(Currency.ARS, Decimal("1")) is money

    def test_convert_to_different_currency(self):
        money_usd = Money(Decimal("2"), Currency.USD)
        converted = money_usd.convert_to(Currency.ARS, Decimal("1000"))

        assert converted.amount == Decimal("2000")
        assert converted.currency == Currency.ARS

    def test_convert_with_non_decimal_type_exchange_rate(self):
        money_usd = Money(Decimal("2"), Currency.USD)
        converted = money_usd.convert_to(Currency.ARS, 1000)

        assert converted.amount == Decimal("2000")
        assert converted.currency == Currency.ARS

    # TODO: qué pasa cuando multiplico un exchange rate decimal
    # TODO: qué pasa cuando cambio de pesos a dólares


class TestMoneyStringRepresentation:
    """Tests de representación en string"""

    @pytest.mark.parametrize(
        "money,result",
        [
            (Money(Decimal("3.50"), Currency.ARS), "3.50 ARS"),
            (Money(Decimal("100"), Currency.USD), "100 USD"),
        ],
    )
    def test_should_return_string_representation(self, money, result):
        assert str(money) == result


class TestMoneyUnaryOperations:
    """Tests de operaciones unarias"""

    def test_should_round_money_to_default_decimals(self):
        money = Money(Decimal("3.14159"), Currency.ARS)

        rounded = round(money)

        assert rounded.amount == Decimal("3")
        assert rounded.currency == Currency.ARS

    def test_should_round_money_to_specified_decimals(self):
        money = Money(Decimal("3.14159"), Currency.ARS)

        rounded = round(money, 2)

        assert rounded.amount == Decimal("3.14")
        assert rounded.currency == Currency.ARS

    def test_should_raise_exception_when_rounding_with_invalid_ndigits(self):
        money = Money(Decimal("3.14159"), Currency.ARS)

        with pytest.raises(TypeError):
            round(money, "2")

    def test_should_raise_exception_when_rounding_with_negative_ndigits(self):
        money = Money(Decimal("3.14159"), Currency.ARS)

        with pytest.raises(ValueError):
            round(money, -1)

    def test_should_return_absolute_value(self):
        money = Money(Decimal("-100"), Currency.ARS)

        abs_money = abs(money)

        assert abs_money.amount == Decimal("100")
        assert abs_money.currency == Currency.ARS

    def test_should_return_negative_value(self):
        money = Money(Decimal("100"), Currency.ARS)

        neg_money = -money

        assert neg_money.amount == Decimal("-100")
        assert neg_money.currency == Currency.ARS

    def test_should_identity_with_positive_operator(self):
        money = Money(Decimal("-100"), Currency.ARS)

        pos_money = +money

        assert pos_money.amount == Decimal("-100")
        assert pos_money.currency == Currency.ARS
