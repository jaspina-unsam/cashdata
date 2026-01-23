import pytest
from decimal import Decimal

from app.domain.value_objects.dual_money import DualMoney
from app.domain.value_objects.money import Currency
from app.domain.exceptions.domain_exceptions import InvalidMoneyOperation


class TestDualMoney:
    def test_single_currency_initialization(self):
        """Test initialization with only primary currency."""
        dm = DualMoney(Decimal('100'), Currency.USD)
        assert dm.primary_amount == Decimal('100')
        assert dm.primary_currency == Currency.USD
        assert dm.secondary_amount is None
        assert dm.secondary_currency is None
        assert dm.exchange_rate is None
        assert not dm.is_dual_currency()

    def test_dual_currency_initialization(self):
        """Test initialization with dual currency."""
        dm = DualMoney(
            Decimal('100'),
            Currency.USD,
            Decimal('85'),
            Currency.ARS,
            Decimal('0.85')
        )
        assert dm.primary_amount == Decimal('100')
        assert dm.primary_currency == Currency.USD
        assert dm.secondary_amount == Decimal('85')
        assert dm.secondary_currency == Currency.ARS
        assert dm.exchange_rate == Decimal('0.85')
        assert dm.is_dual_currency()

    def test_invalid_secondary_amount_without_secondary_currency(self):
        """Test that secondary_amount requires secondary_currency."""
        with pytest.raises(InvalidMoneyOperation, match="secondary_currency required with secondary_amount"):
            DualMoney(Decimal('100'), Currency.USD, Decimal('85'), None, Decimal('0.85'))

    def test_invalid_secondary_amount_without_exchange_rate(self):
        """Test that secondary_amount requires exchange_rate."""
        with pytest.raises(InvalidMoneyOperation, match="exchange_rate is required"):
            DualMoney(Decimal('100'), Currency.USD, Decimal('85'), Currency.ARS, None)

    def test_is_dual_currency_false_for_single(self):
        """Test is_dual_currency returns False for single currency."""
        dm = DualMoney(Decimal('100'), Currency.USD)
        assert not dm.is_dual_currency()

    def test_is_dual_currency_true_for_dual(self):
        """Test is_dual_currency returns True for dual currency."""
        dm = DualMoney(
            Decimal('100'),
            Currency.USD,
            Decimal('85'),
            Currency.ARS,
            Decimal('0.85')
        )
        assert dm.is_dual_currency()

    def test_in_currency_primary(self):
        """Test in_currency returns primary amount for primary currency."""
        dm = DualMoney(
            Decimal('100'),
            Currency.USD,
            Decimal('85'),
            Currency.ARS,
            Decimal('0.85')
        )
        assert dm.in_currency(Currency.USD) == Decimal('100')

    def test_in_currency_secondary(self):
        """Test in_currency returns secondary amount for secondary currency."""
        dm = DualMoney(
            Decimal('100'),
            Currency.USD,
            Decimal('85'),
            Currency.ARS,
            Decimal('0.85')
        )
        assert dm.in_currency(Currency.ARS) == Decimal('85')

    def test_in_currency_not_available(self):
        """Test in_currency raises exception for unavailable currency."""
        dm = DualMoney(Decimal('100'), Currency.USD)
        with pytest.raises(InvalidMoneyOperation, match="Amount not available in"):
            dm.in_currency(Currency.ARS)  # Wait, no, for a currency not present. But Currency only has ARS and USD, so if both are ARS and USD, can't test. Wait, perhaps assume another currency, but since it's StrEnum, maybe add a test with a different currency.

        # Since Currency only has ARS and USD, and the instance has both, to test the exception, I need a currency not in the instance.
        # But the method checks if currency == primary or secondary.
        # To test the else, I need to pass a currency that's neither.
        # But since it's StrEnum, I can create a mock or just use a string, but better to assume we can pass any Currency, but since it's limited, perhaps the test is fine as is.
        # Actually, the method raises if not primary and not secondary.
        # Since the instance has USD and ARS, to test, I need to pass something else, but Currency.ARS is there.
        # Perhaps the test is to pass a currency not in the instance, but since it's dual, both are present.
        # For single currency, pass a different one.
        dm_single = DualMoney(Decimal('100'), Currency.USD)
        with pytest.raises(InvalidMoneyOperation):
            dm_single.in_currency(Currency.ARS)

    def test_in_currency_single_currency(self):
        """Test in_currency for single currency instance."""
        dm = DualMoney(Decimal('100'), Currency.USD)
        assert dm.in_currency(Currency.USD) == Decimal('100')
        with pytest.raises(InvalidMoneyOperation):
            dm.in_currency(Currency.ARS)