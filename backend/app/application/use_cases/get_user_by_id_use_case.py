from app.application.dtos.user_dto import UserResponseDTO
from app.application.exceptions.application_exceptions import UserNotFoundError
from app.application.mappers.user_dto_mapper import UserDTOMapper
from app.domain.repositories import IUnitOfWork


class GetUserByIdUseCase:
    """
    Use case to get an user from database
    """

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, user_id: int) -> UserResponseDTO:
        """
        Retrieves an user from the database given their ID

        Args:
            user_id: User ID

        Returns:
            UserResponseDTO with the user data

        Raises:
            UserNotFoundError if ID is not matching with existing records
        """
        with self._uow:
            user = self._uow.users.find_by_id(user_id)

            if user is None:
                raise UserNotFoundError(
                    f"Given ID {user_id} was not found in database."
                )

            return UserDTOMapper.to_response_dto(user)
