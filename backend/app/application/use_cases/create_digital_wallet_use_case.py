from app.application.dtos.digital_wallet_dto import (
    CreateDigitalWalletInputDTO,
    DigitalWalletResponseDTO,
)
from app.application.exceptions.application_exceptions import UserNotFoundError
from app.application.mappers.digital_wallet_mapper import DigitalWalletDTOMapper
from app.domain.entities.digital_wallet import DigitalWallet
from app.domain.entities.payment_method import PaymentMethod
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.money import Currency
from app.domain.value_objects.payment_method_type import PaymentMethodType


class CreateDigitalWalletUseCase:
    """
    Use case to create a new digital wallet.

    The user_id can be explicitly chosen, which is useful for scenarios where
    someone manages finances for another person (e.g., parents for children,
    accountants for clients, or financial tutors).
    """

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, input_dto: CreateDigitalWalletInputDTO) -> DigitalWalletResponseDTO:
        """
        Execute the use case to create a digital wallet.

        Args:
            input_dto: The input DTO containing digital wallet data, including
                       the user_id of the owner/titular of the wallet
        Returns:
            Created DigitalWallet entity
        Raises:
            UserNotFoundError: If the specified user_id does not exist
        """
        with self._uow as uow:
            # Validate that the user exists
            user = uow.users.find_by_id(input_dto.user_id)
            if not user:
                raise UserNotFoundError(
                    f"User with ID {input_dto.user_id} does not exist"
                )
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
