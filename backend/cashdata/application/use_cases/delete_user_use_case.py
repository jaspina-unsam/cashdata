from cashdata.application.exceptions.application_exceptions import UserNotFoundError
from cashdata.domain.repositories.iunit_of_work import IUnitOfWork


class DeleteUserUseCase:
    """Use case for soft deletion"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, user_id: int) -> None:
        with self._uow:
            user = self._uow.users.find_by_id(user_id)
            if user is None:
                raise UserNotFoundError(user_id)

            user.mark_as_deleted()
            self._uow.users.save(user)
            self._uow.commit()