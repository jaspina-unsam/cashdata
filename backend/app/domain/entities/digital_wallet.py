from dataclasses import dataclass
from typing import Optional

from app.domain.value_objects.money import Currency
from app.domain.exceptions.domain_exceptions import InvalidProviderError


ALLOWED_PROVIDERS = {"mercadopago", "personalpay", "other"}


@dataclass(frozen=True)
class DigitalWallet:
    """Domain entity representing a digital wallet.

    Invariants:
    - name must not be empty
    - provider must be one of allowed providers (case-insensitive)
    - currency must be a valid Currency
    """

    id: Optional[int]
    payment_method_id: int
    user_id: int
    name: str
    provider: str
    identifier: Optional[str]
    currency: Currency = Currency.ARS

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Digital wallet name cannot be empty")

        prov = self.provider.strip().lower() if isinstance(self.provider, str) else ""
        if prov not in ALLOWED_PROVIDERS:
            raise InvalidProviderError(f"Provider '{self.provider}' is not supported")

        # Normalize provider to lowercase
        object.__setattr__(self, "provider", prov)

        if not isinstance(self.currency, Currency):
            object.__setattr__(self, "currency", Currency(self.currency))
