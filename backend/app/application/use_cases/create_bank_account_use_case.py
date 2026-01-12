from app.application.dtos.bank_account_dto import (
    BankAccountResponseDTO,
    CreateBankAccountInputDTO,
)
from app.application.mappers.bank_account_mapper import BankAccountDTOMapper
from app.domain.entities.bank_account import BankAccount
from app.domain.entities.payment_method import PaymentMethod
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.payment_method_type import PaymentMethodType


class CreateBankAccountUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, input_dto: CreateBankAccountInputDTO) -> BankAccountResponseDTO:
        with self._uow as uow:
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
