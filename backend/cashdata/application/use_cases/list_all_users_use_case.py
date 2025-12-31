from typing import List
from cashdata.application.dtos.user_dto import UserResponseDTO
from cashdata.application.mappers.user_dto_mapper import UserDTOMapper
from cashdata.domain.repositories.iunit_of_work import IUnitOfWork


class ListAllUsersUseCase:
    """
    Use case to get all users from database
    """

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self) -> List[UserResponseDTO]:
        """
        Retrieves all users from DB

        Returns:
            List[UserResponseDTO]
        """
        with self._uow:
            users = self._uow.users.find_all()
            return [UserDTOMapper.to_response_dto(u) for u in users]