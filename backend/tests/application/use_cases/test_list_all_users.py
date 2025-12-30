from decimal import Decimal
from unittest.mock import Mock
import pytest

from cashdata.application.use_cases.list_all_users_use_case import ListAllUsersUseCase
from cashdata.domain.entities.user import User
from cashdata.domain.value_objects.money import Currency, Money


@pytest.fixture
def uow_mock():
    uow = Mock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=False)
    uow.users = Mock()
    uow.monthly_incomes = Mock()
    uow.commit = Mock()
    uow.rollback = Mock()

    return uow


@pytest.fixture
def make_user():
    def _make(id, name):
        return User(id, name, f"{name}@mail.com", Money(Decimal("1000"), Currency.USD))
    return _make

@pytest.fixture
def use_case(uow_mock):
    return ListAllUsersUseCase(uow_mock)


class TestListAllUsersUseCase:
    def test_returns_empty_list_when_there_are_zero_users(self, uow_mock, use_case):
        uow_mock.users.find_all.return_value = []

        result = use_case.execute()

        uow_mock.users.find_all.assert_called_once()
        assert result == []

    def test_return_mapped_dtos_when_users_exist(self, uow_mock, make_user, use_case):
        user1 = make_user(1, "Olga")
        user2 = make_user(2, "Margarita")
        user3 = make_user(3, "Marta")
        uow_mock.users.find_all.return_value = [user1, user2, user3]

        result = use_case.execute()

        uow_mock.users.find_all.assert_called_once()
        assert result[0].id == 1
        assert result[1].id == 2
        assert result[2].id == 3

    def test_list_all_does_not_commit(self, make_user, use_case, uow_mock):
        user1 = make_user(1, "Olga")
        uow_mock.users.find_all.return_value = [user1]

        result = use_case.execute()

        uow_mock.users.find_all.assert_called_once()
        uow_mock.commit.assert_not_called()
