from app.application.dtos.cash_account_dto import CreateCashAccountInputDTO, CashAccountResponseDTO
from app.application.exceptions.application_exceptions import UserNotFoundError
from app.application.mappers.cash_account_mapper import CashAccountDTOMapper
from app.domain.entities.cash_account import CashAccount
from app.domain.entities.payment_method import PaymentMethod
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.money import Currency
from app.domain.value_objects.payment_method_type import PaymentMethodType


class CreateCashAccountUseCase:
    """
    Use case to create a new cash account.

    Cash accounts represent physical cash holdings for users.
    The user_id can be explicitly chosen, which is useful for scenarios where
    someone manages finances for another person (e.g., parents for children,
    accountants for clients, or financial tutors).
    """

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, input_dto: CreateCashAccountInputDTO) -> CashAccountResponseDTO:
        """
        Execute the use case to create a cash account.

        Args:
            input_dto: The input DTO containing cash account data, including
                       the user_id of the owner/titular of the account
        Returns:
            Created CashAccount entity
        Raises:
            UserNotFoundError: If the specified user_id does not exist
            ValueError: If a cash account with the same currency already exists
        """
        with self._uow as uow:
            # Validate that the user exists
            user = uow.users.find_by_id(input_dto.user_id)
            if not user:
                raise UserNotFoundError(
                    f"User with ID {input_dto.user_id} does not exist"
                )

            if uow.cash_accounts.exists_by_user_id_and_currency(
                input_dto.user_id, input_dto.currency
            ):
                raise ValueError(
                    "Cash account with this currency already exists for the user."
                )

            payment_method = uow.payment_methods.save(
                PaymentMethod(
                    id=None,
                    user_id=input_dto.user_id,
                    type=PaymentMethodType.CASH,
                    name=input_dto.name,
                )
            )

            cash_account = CashAccount(
                id=None,
                payment_method_id=payment_method.id,
                user_id=input_dto.user_id,
                name=input_dto.name,
                currency=Currency(input_dto.currency),
            )

            saved_cash_account = uow.cash_accounts.save(cash_account)
            uow.commit()

            return CashAccountDTOMapper.to_response_dto(saved_cash_account)
