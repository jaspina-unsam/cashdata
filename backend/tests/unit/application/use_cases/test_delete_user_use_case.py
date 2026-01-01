import pytest
from unittest.mock import MagicMock
from cashdata.application.use_cases.delete_user_use_case import DeleteUserUseCase
from cashdata.application.exceptions.application_exceptions import UserNotFoundError
from cashdata.domain.entities.user import User
from cashdata.domain.value_objects.money import Money, Currency
from decimal import Decimal


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.users = MagicMock()
    return uow


@pytest.fixture
def make_user():
    def _make(
        id, name="Test", email="test@example.com", wage_amount=1000, is_deleted=False
    ):
        return User(
            id=id,
            name=name,
            email=email,
            wage=Money(Decimal(str(wage_amount)), Currency.ARS),
            is_deleted=is_deleted,
        )

    return _make


class TestDeleteUserUseCase:
    def test_delete_successful(self, mock_uow, make_user):
        # Arrange
        user = make_user(1)
        mock_uow.users.find_by_id.return_value = user
        use_case = DeleteUserUseCase(mock_uow)

        # Act
        use_case.execute(1)

        # Assert
        mock_uow.users.find_by_id.assert_called_once_with(1)
        assert user.is_deleted == True
        mock_uow.users.save.assert_called_once_with(user)
        mock_uow.commit.assert_called_once()

    def test_user_not_found(self, mock_uow):
        # Arrange
        mock_uow.users.find_by_id.return_value = None
        use_case = DeleteUserUseCase(mock_uow)

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            use_case.execute(1)

        mock_uow.users.find_by_id.assert_called_once_with(1)
        mock_uow.users.save.assert_not_called()
        mock_uow.commit.assert_not_called()

    def test_already_deleted(self, mock_uow, make_user):
        # Arrange
        user = make_user(1, is_deleted=True)
        mock_uow.users.find_by_id.return_value = user
        use_case = DeleteUserUseCase(mock_uow)

        # Act
        use_case.execute(1)

        # Assert
        # Even if already deleted, it remains deleted
        assert user.is_deleted == True
        mock_uow.users.save.assert_called_once_with(user)
        mock_uow.commit.assert_called_once()

    def test_commit_called(self, mock_uow, make_user):
        # Arrange
        user = make_user(1)
        mock_uow.users.find_by_id.return_value = user
        use_case = DeleteUserUseCase(mock_uow)

        # Act
        use_case.execute(1)

        # Assert
        mock_uow.commit.assert_called_once()
