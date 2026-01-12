from app.domain.entities.digital_wallet import DigitalWallet
from app.application.dtos.digital_wallet_dto import DigitalWalletResponseDTO


class DigitalWalletDTOMapper:
    @staticmethod
    def to_response_dto(wallet: DigitalWallet) -> DigitalWalletResponseDTO:
        return DigitalWalletResponseDTO(
            id=wallet.id,
            payment_method_id=wallet.payment_method_id,
            user_id=wallet.user_id,
            name=wallet.name,
            provider=wallet.provider,
            identifier=wallet.identifier,
            currency=wallet.currency,
        )
