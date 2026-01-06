from app.application.dtos.user_dto import UpdateUserInputDTO, UserResponseDTO
from app.application.exceptions.application_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.infrastructure.persistence.mappers.user_dto_mapper import UserDTOMapper
from app.domain.entities.user import User
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.money import Money


class UpdateUserUseCase:
    """
    Use case to update a given user
    """

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, input_dto: UpdateUserInputDTO) -> UserResponseDTO:
        """
        Updates an existing user

        Args:
            input_dto: Validated user data

        Returns:
            UserResponseDTO: Updated user data

        Raises:
            UserAlreadyExistsError: If email already exists
            UserNotFoundError: If no user exists with the given ID
        """
        with self._uow:
            user = self._uow.users.find_by_id(input_dto.id)
            if not user:
                raise UserNotFoundError(f"User with ID {input_dto.id} not found")
            if input_dto.email and input_dto.email != user.email:
                if self._uow.users.exists_by_email(input_dto.email):
                    raise UserAlreadyExistsError(input_dto.email)

            updated_user = User(
                id=user.id,
                name=input_dto.name if input_dto.name is not None else user.name,
                email=input_dto.email if input_dto.email else user.email,
                wage=Money(
                    amount=(
                        input_dto.wage_amount
                        if input_dto.wage_amount is not None
                        else user.wage.amount
                    ),
                    currency=(
                        input_dto.wage_currency
                        if input_dto.wage_currency is not None
                        else user.wage.currency
                    ),
                ),
            )
            saved_user = self._uow.users.save(updated_user)
            self._uow.commit()

            return UserDTOMapper.to_response_dto(saved_user)
