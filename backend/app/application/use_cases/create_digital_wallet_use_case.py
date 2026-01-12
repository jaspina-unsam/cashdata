from app.application.dtos.digital_wallet_dto import (
    CreateDigitalWalletInputDTO,
    DigitalWalletResponseDTO,
)
from app.application.mappers.digital_wallet_mapper import DigitalWalletDTOMapper
from app.domain.entities.digital_wallet import DigitalWallet
from app.domain.entities.payment_method import PaymentMethod
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.money import Currency
from app.domain.value_objects.payment_method_type import PaymentMethodType


class CreateDigitalWalletUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, input_dto: CreateDigitalWalletInputDTO) -> DigitalWalletResponseDTO:
        with self._uow as uow:
            # Create payment method first
            payment_method = uow.payment_methods.save(
                PaymentMethod(
                    id=None,
                    user_id=input_dto.user_id,
                    type=PaymentMethodType.DIGITAL_WALLET,
                    name=input_dto.name,
                )
            )

            wallet = DigitalWallet(
                id=None,
                payment_method_id=payment_method.id,
                user_id=input_dto.user_id,
                name=input_dto.name,
                provider=input_dto.provider,
                identifier=input_dto.identifier,
                currency=Currency(input_dto.currency),
            )

            saved = uow.digital_wallets.save(wallet)
            uow.commit()
            return DigitalWalletDTOMapper.to_response_dto(saved)
