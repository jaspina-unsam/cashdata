from app.domain.entities.digital_wallet import DigitalWallet
from app.domain.value_objects.money import Currency
from app.infrastructure.persistence.models.digital_wallet_model import DigitalWalletModel


class DigitalWalletMapper:
    @staticmethod
    def to_entity(model: DigitalWalletModel) -> DigitalWallet:
        return DigitalWallet(
            id=model.id,
            payment_method_id=model.payment_method_id,
            user_id=model.user_id,
            name=model.name,
            provider=model.provider,
            identifier=model.identifier,
            currency=Currency(model.currency),
        )

    @staticmethod
    def to_model(entity: DigitalWallet) -> DigitalWalletModel:
        model = DigitalWalletModel(
            id=entity.id,
            payment_method_id=entity.payment_method_id,
            user_id=entity.user_id,
            name=entity.name,
            provider=entity.provider,
            identifier=entity.identifier,
            currency=entity.currency.value,
        )
        return model
