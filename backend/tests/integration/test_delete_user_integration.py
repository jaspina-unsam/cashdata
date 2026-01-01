# tests/integration/test_delete_user_integration.py
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cashdata.application.use_cases.delete_user_use_case import DeleteUserUseCase
from cashdata.application.use_cases.create_user_use_case import CreateUserUseCase
from cashdata.application.dtos.user_dto import CreateUserInputDTO
from cashdata.domain.entities.user import User
from cashdata.domain.value_objects.money import Currency
from cashdata.infrastructure.persistence.models.user_model import UserModel
from cashdata.infrastructure.persistence.repositories.sqlalchemy_unit_of_work import (
    SQLAlchemyUnitOfWork,
)


@pytest.fixture
def session_factory():
    """
    Crea una base de datos SQLite en memoria para tests.
    Se destruye al finalizar cada test.
    """
    engine = create_engine("sqlite:///:memory:")
    UserModel.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine)
    yield SessionFactory


class TestDeleteUserUseCaseIntegration:
    """
    Integration tests con base de datos real.

    Propósito: Validar que el stack funciona end-to-end:
    - Use Case → UoW → Repository → SQLAlchemy → Database
    """

    def test_delete_user_end_to_end(self, session_factory):
        """
        GIVEN: Usuario existente en DB
        WHEN: Ejecuto delete use case
        THEN: Usuario se marca como deleted y no aparece en queries
        """
        # Arrange
        uow = SQLAlchemyUnitOfWork(session_factory)
        create_use_case = CreateUserUseCase(uow)
        delete_use_case = DeleteUserUseCase(uow)

        input_dto = CreateUserInputDTO(
            name="Test User",
            email="test@example.com",
            wage_amount=Decimal("1000"),
            wage_currency=Currency.ARS,
        )

        # Create user
        created_user = create_use_case.execute(input_dto)
        user_id = created_user.id

        # Act
        delete_use_case.execute(user_id)

        # Assert
        # User should not be found by id
        with uow:
            found_user = uow.users.find_by_id(user_id)
            assert found_user is None

        # User should not appear in find_all
        with uow:
            all_users = uow.users.find_all()
            assert len(all_users) == 0

    def test_user_not_appears_in_find_all_after_delete(self, session_factory):
        """
        GIVEN: Múltiples usuarios, uno deleted
        WHEN: Consulto find_all
        THEN: Solo usuarios no deleted aparecen
        """
        # Arrange
        uow = SQLAlchemyUnitOfWork(session_factory)
        create_use_case = CreateUserUseCase(uow)
        delete_use_case = DeleteUserUseCase(uow)

        # Create two users
        input_dto1 = CreateUserInputDTO(
            name="User 1",
            email="user1@example.com",
            wage_amount=Decimal("1000"),
            wage_currency=Currency.ARS,
        )
        input_dto2 = CreateUserInputDTO(
            name="User 2",
            email="user2@example.com",
            wage_amount=Decimal("2000"),
            wage_currency=Currency.ARS,
        )

        user1 = create_use_case.execute(input_dto1)
        user2 = create_use_case.execute(input_dto2)

        # Delete one
        delete_use_case.execute(user1.id)

        # Assert
        with uow:
            all_users = uow.users.find_all()
            assert len(all_users) == 1
            assert all_users[0].id == user2.id

    def test_find_by_id_returns_none_after_delete(self, session_factory):
        """
        GIVEN: Usuario deleted
        WHEN: Consulto find_by_id
        THEN: Retorna None
        """
        # Arrange
        uow = SQLAlchemyUnitOfWork(session_factory)
        create_use_case = CreateUserUseCase(uow)
        delete_use_case = DeleteUserUseCase(uow)

        input_dto = CreateUserInputDTO(
            name="Test User",
            email="test@example.com",
            wage_amount=Decimal("1000"),
            wage_currency=Currency.ARS,
        )

        created_user = create_use_case.execute(input_dto)
        user_id = created_user.id

        # Delete
        delete_use_case.execute(user_id)

        # Assert
        with uow:
            found_user = uow.users.find_by_id(user_id)
            assert found_user is None
