import pytest
from unittest.mock import Mock

from cashdata.application.use_cases.get_user_by_id_use_case import (
    GetUserByIdUseCase,
)
from cashdata.application.dtos.user_dto import UserResponseDTO
from cashdata.application.exceptions.application_exceptions import (
    UserNotFoundError,
)
from cashdata.domain.entities.user import User
from cashdata.domain.value_objects.money import Money, Currency


class TestGetUserByIdUseCase:
    def test_returns_user_when_exists(self):
        uow = Mock()
        uow.__enter__ = Mock(return_value=uow)
        uow.__exit__ = Mock(return_value=False)
        uow.users = Mock()
        uow.commit = Mock()

        # Arrange: repository returns a User entity
        user = User(
            id=1,
            name="Exists User",
            email="exists@test.com",
            wage=Money(1000, Currency.ARS),
        )
        uow.users.find_by_id.return_value = user

        use_case = GetUserByIdUseCase(uow)

        # Act
        result = use_case.execute(1)

        # Assert
        assert isinstance(result, UserResponseDTO)
        assert result.id == 1
        assert result.name == "Exists User"
        assert result.email == "exists@test.com"
        assert result.wage_amount == user.wage.amount
        assert result.wage_currency == user.wage.currency

    def test_raises_error_when_not_found(self):
        uow = Mock()
        uow.__enter__ = Mock(return_value=uow)
        uow.__exit__ = Mock(return_value=False)
        uow.users = Mock()
        uow.commit = Mock()

        uow.users.find_by_id.return_value = None

        use_case = GetUserByIdUseCase(uow)

        with pytest.raises(UserNotFoundError) as exc_info:
            use_case.execute(999)

        assert "999" in str(exc_info.value)

    def test_does_not_call_commit(self):
        uow = Mock()
        uow.__enter__ = Mock(return_value=uow)
        uow.__exit__ = Mock(return_value=False)
        uow.users = Mock()
        uow.commit = Mock()

        user = User(
            id=2,
            name="No Commit",
            email="nocommit@test.com",
            wage=Money(1, Currency.ARS),
        )

        uow.users.find_by_id.return_value = user

        use_case = GetUserByIdUseCase(uow)
        use_case.execute(2)

        # Reading should not trigger a commit
        uow.commit.assert_not_called()
