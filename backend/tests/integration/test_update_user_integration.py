# tests/integration/test_update_user_integration.py
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.use_cases.create_user_use_case import CreateUserUseCase
from app.application.use_cases.update_user_use_case import UpdateUserUseCase
from app.application.dtos.user_dto import CreateUserInputDTO, UpdateUserInputDTO
from app.application.exceptions.application_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.domain.value_objects.money import Currency
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.repositories.sqlalchemy_unit_of_work import (
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


class TestUpdateUserUseCaseIntegration:
    """
    Integration tests con base de datos real.

    Propósito: Validar que el stack funciona end-to-end:
    - Use Case → UoW → Repository → SQLAlchemy → Database
    """

    def test_update_user_successful(self, session_factory):
        """
        GIVEN: Usuario existe en la base de datos
        WHEN: Actualizo sus datos
        THEN: Los cambios se persisten correctamente y se puede recuperar el usuario actualizado

        Este test valida el flujo completo de actualización exitosa.
        """
        # Arrange - Crear usuario inicial
        uow = SQLAlchemyUnitOfWork(session_factory)
        create_use_case = CreateUserUseCase(uow)

        create_dto = CreateUserInputDTO(
            name="Juan Pérez",
            email="juan@test.com",
            wage_amount=Decimal("50000.00"),
            wage_currency=Currency.ARS,
        )
        created_user = create_use_case.execute(create_dto)

        # Arrange - Preparar actualización
        update_uow = SQLAlchemyUnitOfWork(session_factory)
        update_use_case = UpdateUserUseCase(update_uow)

        update_dto = UpdateUserInputDTO(
            id=created_user.id,
            name="Juan Pérez Actualizado",
            email="juan.actualizado@test.com",
            wage_amount=Decimal("75000.00"),
            wage_currency=Currency.ARS,
        )

        # Act
        result = update_use_case.execute(update_dto)

        # Assert - Verificar DTO de respuesta
        assert result.id == created_user.id
        assert result.name == "Juan Pérez Actualizado"
        assert result.email == "juan.actualizado@test.com"
        assert result.wage_amount == Decimal("75000.00")
        assert result.wage_currency == Currency.ARS

        # Assert - Verificar persistencia real
        with SQLAlchemyUnitOfWork(session_factory) as verify_uow:
            saved_user = verify_uow.users.find_by_id(created_user.id)
            assert saved_user is not None
            assert saved_user.name == "Juan Pérez Actualizado"
            assert saved_user.email == "juan.actualizado@test.com"
            assert saved_user.wage.amount == Decimal("75000.00")
            assert saved_user.wage.currency == Currency.ARS

    def test_duplicate_email_prevents_update(self, session_factory):
        """
        GIVEN: Dos usuarios existen, uno con email que quiero usar
        WHEN: Intento actualizar el email de uno al email del otro
        THEN: Lanza UserAlreadyExistsError y no se actualiza
        """
        # Arrange - Crear dos usuarios
        uow = SQLAlchemyUnitOfWork(session_factory)
        create_use_case = CreateUserUseCase(uow)

        # Usuario 1
        user1_dto = CreateUserInputDTO(
            name="Usuario Uno",
            email="usuario1@test.com",
            wage_amount=Decimal("50000"),
            wage_currency=Currency.ARS,
        )
        user1 = create_use_case.execute(user1_dto)

        # Usuario 2
        user2_dto = CreateUserInputDTO(
            name="Usuario Dos",
            email="usuario2@test.com",
            wage_amount=Decimal("60000"),
            wage_currency=Currency.ARS,
        )
        user2 = create_use_case.execute(user2_dto)

        # Arrange - Intentar actualizar usuario1 con email de usuario2
        update_uow = SQLAlchemyUnitOfWork(session_factory)
        update_use_case = UpdateUserUseCase(update_uow)

        update_dto = UpdateUserInputDTO(
            id=user1.id,
            name=None,
            email="usuario2@test.com",  # Email que ya existe
            wage_amount=None,
            wage_currency=None,
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            update_use_case.execute(update_dto)

        # Verificar mensaje de error
        assert "usuario2@test.com" in str(exc_info.value)

        # Assert - Verificar que NO se actualizó (datos originales intactos)
        with SQLAlchemyUnitOfWork(session_factory) as verify_uow:
            unchanged_user = verify_uow.users.find_by_id(user1.id)
            assert unchanged_user.name == "Usuario Uno"
            assert unchanged_user.email == "usuario1@test.com"
            assert unchanged_user.wage.amount == Decimal("50000")

    def test_correct_persistence(self, session_factory):
        """
        GIVEN: Usuario existe con ciertos datos
        WHEN: Actualizo parcialmente (solo algunos campos)
        THEN: Solo los campos especificados cambian, los demás permanecen iguales

        Este test valida que la persistencia respeta los valores None (no actualizar).
        """
        # Arrange - Crear usuario inicial
        uow = SQLAlchemyUnitOfWork(session_factory)
        create_use_case = CreateUserUseCase(uow)

        create_dto = CreateUserInputDTO(
            name="María García",
            email="maria@test.com",
            wage_amount=Decimal("55000.00"),
            wage_currency=Currency.ARS,
        )
        created_user = create_use_case.execute(create_dto)

        # Arrange - Actualizar solo el nombre y email, mantener salario
        update_uow = SQLAlchemyUnitOfWork(session_factory)
        update_use_case = UpdateUserUseCase(update_uow)

        update_dto = UpdateUserInputDTO(
            id=created_user.id,
            name="María García Actualizada",  # Cambiar nombre
            email="maria.actualizada@test.com",  # Cambiar email
            wage_amount=None,  # NO cambiar salario
            wage_currency=None,  # NO cambiar moneda
        )

        # Act
        result = update_use_case.execute(update_dto)

        # Assert - Verificar respuesta
        assert result.name == "María García Actualizada"
        assert result.email == "maria.actualizada@test.com"
        assert result.wage_amount == Decimal("55000.00")  # Debe mantenerse igual
        assert result.wage_currency == Currency.ARS  # Debe mantenerse igual

        # Assert - Verificar persistencia en DB
        with SQLAlchemyUnitOfWork(session_factory) as verify_uow:
            persisted_user = verify_uow.users.find_by_id(created_user.id)
            assert persisted_user.name == "María García Actualizada"
            assert persisted_user.email == "maria.actualizada@test.com"
            assert persisted_user.wage.amount == Decimal("55000.00")  # Sin cambios
            assert persisted_user.wage.currency == Currency.ARS  # Sin cambios