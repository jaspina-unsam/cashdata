# backend/cashdata/application/use_cases/create_user_use_case.py
from app.domain.repositories import IUnitOfWork
from app.domain.entities.user import User
from app.domain.value_objects.money import Money, Currency
from app.application.dtos.user_dto import CreateUserInputDTO, UserResponseDTO
from app.infrastructure.persistence.mappers.user_dto_mapper import UserDTOMapper
from app.application.exceptions.application_exceptions import (
    UserAlreadyExistsError,
)


class CreateUserUseCase:
    """Use case for creating a new user with validation"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, input_dto: CreateUserInputDTO) -> UserResponseDTO:
        """
        Create a new user with validation

        Args:
            input_dto: Validated user creation data

        Returns:
            UserResponseDTO: Created user data

        Raises:
            UserAlreadyExistsError: If email already exists
        """
        with self._uow:
            # 1. Validate email uniqueness
            if self._uow.users.exists_by_email(input_dto.email):
                raise UserAlreadyExistsError(input_dto.email)

            # 2. Create User entity with Money value object
            user = User(
                id=None,  # DB generates ID
                name=input_dto.name,
                email=input_dto.email,
                wage=Money(input_dto.wage_amount, Currency(input_dto.wage_currency)),
            )

            # 3. Persist with UoW (atomic transaction)
            saved_user = self._uow.users.save(user)
            self._uow.commit()

        # 4. Map to response DTO and return
        return UserDTOMapper.to_response_dto(saved_user)
