import pytest
from app.domain.entities.digital_wallet import DigitalWallet
from app.domain.exceptions.domain_exceptions import InvalidProviderError
from app.domain.value_objects.money import Currency


def test_create_valid_digital_wallet():
    wallet = DigitalWallet(
        id=None,
        payment_method_id=1,
        user_id=1,
        name="My Wallet",
        provider="mercadopago",
        identifier="user_123",
        currency=Currency.ARS,
    )

    assert wallet.provider == "mercadopago"
    assert wallet.name == "My Wallet"


def test_invalid_provider_raises():
    with pytest.raises(InvalidProviderError):
        DigitalWallet(
            id=None,
            payment_method_id=1,
            user_id=1,
            name="X",
            provider="unsupported_provider",
            identifier=None,
            currency=Currency.ARS,
        )
