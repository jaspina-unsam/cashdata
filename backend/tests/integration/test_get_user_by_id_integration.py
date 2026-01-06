import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.use_cases.get_user_by_id_use_case import (
    GetUserByIdUseCase,
)
from app.application.exceptions.application_exceptions import (
    UserNotFoundError,
)
from app.domain.entities.user import User
from app.domain.value_objects.money import Money, Currency
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


class TestGetUserByIdIntegration:
    def test_get_user_end_to_end(self, session_factory):
        # Arrange - persist a user via real UoW
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            user = User(
                id=None,
                name="Integration User",
                email="integration@get.com",
                wage=Money(Decimal("42000.00"), Currency.ARS),
            )
            saved_user = uow.users.save(user)
            uow.commit()
            saved_id = saved_user.id

        # Act - use case to retrieve
        use_case = GetUserByIdUseCase(SQLAlchemyUnitOfWork(session_factory))
        result = use_case.execute(saved_id)

        # Assert
        assert result.id == saved_id
        assert result.name == "Integration User"
        assert result.email == "integration@get.com"
        assert result.wage_amount == Decimal("42000.00")

    def test_error_for_nonexistent_user(self, session_factory):
        use_case = GetUserByIdUseCase(SQLAlchemyUnitOfWork(session_factory))

        with pytest.raises(UserNotFoundError):
            use_case.execute(99999)
