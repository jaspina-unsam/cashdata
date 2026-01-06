import pytest
from decimal import Decimal
from app.domain.entities.user import User
from app.domain.value_objects.money import Money, Currency
from app.domain.exceptions.domain_exceptions import InvalidEntity


@pytest.fixture
def make_user():
    def _make(id, name, email, wage_amount, wage_currency=Currency.ARS):
        return User(
            id=id,
            name=name,
            email=email,
            wage=Money(Decimal(str(wage_amount)), wage_currency),
        )

    return _make


class TestUserCreation:
    def test_should_create_user_with_valid_data(self, make_user):
        test_user = make_user(1, "Test", "t@example.com", 1000)

        assert str(test_user) == "User(Test, t@example.com)"

    def test_should_raise_when_name_is_empty(self, make_user):
        with pytest.raises(InvalidEntity) as edesc:
            _ = make_user(1, "", "empty@email.com", 1000)

        assert "name cannot be empty" in str(edesc).lower()

    def test_should_raise_when_email_is_invalid(self, make_user):
        with pytest.raises(InvalidEntity) as edesc:
            _ = make_user(1, "Test", "invalid", 1000)

        assert "invalid email format" in str(edesc).lower()


class TestUserEquality:
    """Tests de igualdad"""

    def test_should_be_equal_when_same_id(self, make_user):
        test_user1 = make_user(1, "test1", "t1@example.com", 1000)
        test_user2 = make_user(1, "test2", "t2@example.com", 1100)

        assert test_user1 == test_user2

    def test_should_not_be_equal_when_different_id(self, make_user):
        test_user1 = make_user(1, "test1", "t1@example.com", 1000)
        test_user2 = make_user(2, "test2", "t2@example.com", 1100)

        assert test_user1 != test_user2


class TestUserMutability:
    """Tests de mutabilidad"""

    def test_should_update_wage(self, make_user):
        test_user = make_user(1, "Test", "t@example.com", 1000)
        new_wage = Money("2000", Currency.USD)
        test_user.update_wage(new_wage)

        assert test_user.wage == new_wage

    def test_should_update_name(self, make_user):
        test_user = make_user(1, "Test", "t@example.com", 1000)
        new_name = "Carlos"
        test_user.update_name(new_name)

        assert test_user.name == new_name

    def test_should_update_email(self, make_user):
        test_user = make_user(1, "Test", "t@example.com", 1000)
        new_email = "test@example.com"
        test_user.update_email(new_email)

        assert test_user.email == new_email


class TestUserHash:
    """Tests de hash (para usar en sets/dicts)"""

    def test_should_be_hashable(self, make_user):
        test_user = make_user(1, "test", "t@example.com", 1000)
        users_set = {test_user}
        assert test_user in users_set
