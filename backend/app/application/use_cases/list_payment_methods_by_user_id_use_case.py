from typing import List
from app.application.dtos.payment_method_dto import PaymentMethodResponseDTO
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.application.mappers.payment_method_mapper import PaymentMethodDTOMapper


class ListPaymentMethodsByUserIdUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, user_id: int) -> List[PaymentMethodResponseDTO]:
        """
        Retrieves all payment methods owned by the user from DB

        Returns:
            List[PaymentMethodResponseDTO]
        """
        with self._uow as uow:
            payment_methods = uow.payment_methods.find_by_user_id(user_id)
            return [PaymentMethodDTOMapper.to_response_dto(pm) for pm in payment_methods]