from app.application.dtos.cash_account_dto import CreateCashAccountInputDTO, CashAccountResponseDTO
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
    """

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, input_dto: CreateCashAccountInputDTO) -> CashAccountResponseDTO:
        """
        Execute the use case to create a cash account.

        Args:
            input_dto: The input DTO containing cash account data
        Returns:
            Created CashAccount entity
        """
        with self._uow as uow:
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
