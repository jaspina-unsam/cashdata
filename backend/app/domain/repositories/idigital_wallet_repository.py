from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.digital_wallet import DigitalWallet


class IDigitalWalletRepository(ABC):
    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[DigitalWallet]:
        pass

    @abstractmethod
    def find_by_id(self, wallet_id: int) -> DigitalWallet | None:
        pass

    @abstractmethod
    def save(self, digital_wallet: DigitalWallet) -> DigitalWallet:
        pass

    @abstractmethod
    def delete(self, digital_wallet: DigitalWallet) -> None:
        pass

    @abstractmethod
    def exists_by_payment_method_id(self, payment_method_id: int) -> bool:
        pass
from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.digital_wallet import DigitalWallet


class IDigitalWalletRepository(ABC):
    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[DigitalWallet]:
        pass

    @abstractmethod
    def find_by_id(self, wallet_id: int) -> DigitalWallet | None:
        pass

    @abstractmethod
    def save(self, digital_wallet: DigitalWallet) -> DigitalWallet:
        pass

    @abstractmethod
    def delete(self, digital_wallet: DigitalWallet) -> None:
        pass

    @abstractmethod
    def exists_by_payment_method_id(self, payment_method_id: int) -> bool:
        pass
