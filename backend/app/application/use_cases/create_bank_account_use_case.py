from app.application.dtos.bank_account_dto import (
    BankAccountResponseDTO,
    CreateBankAccountInputDTO,
)
from app.application.exceptions.application_exceptions import UserNotFoundError
from app.application.mappers.bank_account_mapper import BankAccountDTOMapper
from app.domain.entities.bank_account import BankAccount
from app.domain.entities.payment_method import PaymentMethod
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.payment_method_type import PaymentMethodType


class CreateBankAccountUseCase:
    """
    Use case to create a new bank account.

    Bank accounts can have one or two owners (primary and optional secondary user).
    The primary_user_id and secondary_user_id can be explicitly chosen, which is
    useful for scenarios where someone manages finances for another person or for
    joint accounts (e.g., spouses, family members).
    """

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, input_dto: CreateBankAccountInputDTO) -> BankAccountResponseDTO:
        """
        Execute the use case to create a bank account.

        Args:
            input_dto: The input DTO containing bank account data, including
                       primary_user_id and optional secondary_user_id
        Returns:
            Created BankAccount entity
        Raises:
            UserNotFoundError: If either primary_user_id or secondary_user_id
                               does not exist
        """
        with self._uow as uow:
            # Validate that the primary user exists
            primary_user = uow.users.find_by_id(input_dto.primary_user_id)
            if not primary_user:
                raise UserNotFoundError(
                    f"Primary user with ID {input_dto.primary_user_id} does not exist"
                )

            # Validate that the secondary user exists (if provided)
            if input_dto.secondary_user_id is not None:
                secondary_user = uow.users.find_by_id(input_dto.secondary_user_id)
                if not secondary_user:
                    raise UserNotFoundError(
                        f"Secondary user with ID {input_dto.secondary_user_id} does not exist"
                    )
            payment_method = uow.payment_methods.save(
                PaymentMethod(
                    id=None,
                    user_id=input_dto.primary_user_id,
                    type=PaymentMethodType.BANK_ACCOUNT,
                    name=input_dto.name,
                )
            )

            account = BankAccount(
                id=None,
                payment_method_id=payment_method.id,
                primary_user_id=input_dto.primary_user_id,
                secondary_user_id=input_dto.secondary_user_id,
                name=input_dto.name,
                bank=input_dto.bank,
                account_type=input_dto.account_type,
                last_four_digits=input_dto.last_four_digits,
                currency=input_dto.currency,
            )

            saved_account = uow.bank_accounts.save(account)
            uow.commit()

            return BankAccountDTOMapper.to_response_dto(saved_account)
