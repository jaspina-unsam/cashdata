from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.use_cases.list_all_users_use_case import ListAllUsersUseCase
from app.domain.entities.user import User
from app.domain.value_objects.money import Currency, Money
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.repositories.sqlalchemy_unit_of_work import (
    SQLAlchemyUnitOfWork,
)


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite:///:memory:")
    UserModel.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine)
    yield SessionFactory


class TestListAllUsersIntegration:
    def test_list_returns_empty_list_with_zero_users(self, session_factory):
        use_case = ListAllUsersUseCase(SQLAlchemyUnitOfWork(session_factory))

        result = use_case.execute()

        assert len(result) == 0

    def test_list_all_created_users(self, session_factory):
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            user1 = User(
                id=None,
                name="Integration User",
                email="integration@get.com",
                wage=Money(Decimal("42000.00"), Currency.ARS),
            )
            uow.users.save(user1)
            user2 = User(
                id=None,
                name="Integration User 2",
                email="integration2@get.com",
                wage=Money(Decimal("42000.00"), Currency.ARS),
            )
            uow.users.save(user2)
            uow.commit()
        use_case = ListAllUsersUseCase(SQLAlchemyUnitOfWork(session_factory))

        result = use_case.execute()

        assert len(result) == 2
