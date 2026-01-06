# tests/application/use_cases/test_update_user_use_case.py
import pytest
from unittest.mock import Mock
from decimal import Decimal

from app.application.use_cases.create_user_use_case import CreateUserUseCase
from app.application.use_cases.update_user_use_case import UpdateUserUseCase
from app.application.dtos.user_dto import CreateUserInputDTO, UpdateUserInputDTO, UserResponseDTO
from app.application.exceptions.application_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.domain.entities.user import User
from app.domain.value_objects.money import Money, Currency


@pytest.fixture
def uow_mock():
    """
    Mock del UnitOfWork para aislar el use case.

    Simula el comportamiento del context manager (__enter__ / __exit__)
    """
    uow = Mock()

    # Simular context manager
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=False)

    # Simular repositories
    uow.users = Mock()
    uow.monthly_incomes = Mock()

    # Métodos del UoW
    uow.commit = Mock()
    uow.rollback = Mock()

    return uow


@pytest.fixture
def existing_user():
    """Usuario existente para tests"""
    return User(
        id=1,
        name="Juan Pérez",
        email="juan@example.com",
        wage=Money(Decimal("50000.00"), Currency.ARS),
    )


@pytest.fixture
def update_use_case(uow_mock):
    """Instancia del use case con UoW mockeado"""
    return UpdateUserUseCase(uow_mock)


@pytest.fixture
def create_use_case(uow_mock):
    """Instancia del use case con UoW mockeado"""
    return CreateUserUseCase(uow_mock)

@pytest.fixture
def valid_create_input_dto():
    """DTO de entrada válido para tests"""
    return CreateUserInputDTO(
        name="Juan Pérez",
        email="juan@example.com",
        wage_amount=Decimal("50000.00"),
        wage_currency=Currency.ARS,
    )


class TestUpdateUserUseCase:
    """
    Unit tests for UpdateUserUseCase using mocks.

    Propósito: Validar la LÓGICA del use case sin dependencias externas.
    """

    def test_partial_update_user_name(
        self, create_use_case, update_use_case, uow_mock, existing_user, valid_create_input_dto
    ):
        """
        GIVEN: Usuario existe y quiero actualizar solo el nombre
        WHEN: Ejecuto el use case con solo name
        THEN: Se actualiza el nombre, se mantiene el resto y retorna DTO actualizado
        """
        # Arrange
        uow_mock.users.find_by_id.return_value = existing_user
        uow_mock.users.save.return_value = User(
            id=1,
            name="María García",  # Nuevo nombre
            email="juan@example.com",  # Mismo email
            wage=Money(Decimal("50000.00"), Currency.ARS),  # Mismo salario
        )

        update_dto = UpdateUserInputDTO(
            id=1,
            name="María García",
            email=None,
            wage_amount=None,
            wage_currency=None,
        )

        # Act
        result = update_use_case.execute(update_dto)

        # Assert - Verificar llamadas
        uow_mock.users.find_by_id.assert_called_once_with(1)
        uow_mock.users.save.assert_called_once()
        uow_mock.commit.assert_called_once()

        # Assert - Verificar resultado
        assert isinstance(result, UserResponseDTO)
        assert result.id == 1
        assert result.name == "María García"
        assert result.email == "juan@example.com"  # No cambió
        assert result.wage_amount == Decimal("50000.00")
        assert result.wage_currency == Currency.ARS

    def test_partial_update_user_email(self, update_use_case, uow_mock, existing_user):
        """
        GIVEN: Usuario existe y quiero actualizar solo el email
        WHEN: Ejecuto el use case con solo email nuevo
        THEN: Se valida unicidad, se actualiza el email y retorna DTO actualizado
        """
        # Arrange
        uow_mock.users.find_by_id.return_value = existing_user
        uow_mock.users.exists_by_email.return_value = False  # Email nuevo no existe

        updated_user = User(
            id=1,
            name="Juan Pérez",  # Mismo nombre
            email="juan.nuevo@example.com",  # Nuevo email
            wage=Money(Decimal("50000.00"), Currency.ARS),  # Mismo salario
        )
        uow_mock.users.save.return_value = updated_user

        update_dto = UpdateUserInputDTO(
            id=1,
            name=None,
            email="juan.nuevo@example.com",
            wage_amount=None,
            wage_currency=None,
        )

        # Act
        result = update_use_case.execute(update_dto)

        # Assert - Verificar llamadas
        uow_mock.users.find_by_id.assert_called_once_with(1)
        uow_mock.users.exists_by_email.assert_called_once_with("juan.nuevo@example.com")
        uow_mock.users.save.assert_called_once()
        uow_mock.commit.assert_called_once()

        # Assert - Verificar resultado
        assert result.email == "juan.nuevo@example.com"
        assert result.name == "Juan Pérez"  # No cambió
        assert result.wage_amount == Decimal("50000.00")

    def test_update_user_multiple_fields(self, update_use_case, uow_mock, existing_user):
        """
        GIVEN: Usuario existe y quiero actualizar nombre, email y salario
        WHEN: Ejecuto el use case con múltiples campos
        THEN: Se actualizan todos los campos y retorna DTO actualizado
        """
        # Arrange
        uow_mock.users.find_by_id.return_value = existing_user
        uow_mock.users.exists_by_email.return_value = False  # Email nuevo no existe

        updated_user = User(
            id=1,
            name="Carlos Rodríguez",
            email="carlos@example.com",
            wage=Money(Decimal("75000.00"), Currency.ARS),
        )
        uow_mock.users.save.return_value = updated_user

        update_dto = UpdateUserInputDTO(
            id=1,
            name="Carlos Rodríguez",
            email="carlos@example.com",
            wage_amount=Decimal("75000.00"),
            wage_currency=Currency.ARS,
        )

        # Act
        result = update_use_case.execute(update_dto)

        # Assert - Verificar llamadas
        uow_mock.users.find_by_id.assert_called_once_with(1)
        uow_mock.users.exists_by_email.assert_called_once_with("carlos@example.com")
        uow_mock.users.save.assert_called_once()
        uow_mock.commit.assert_called_once()

        # Assert - Verificar resultado
        assert result.name == "Carlos Rodríguez"
        assert result.email == "carlos@example.com"
        assert result.wage_amount == Decimal("75000.00")
        assert result.wage_currency == Currency.ARS

    def test_email_unchanged_does_not_validate_uniqueness(
        self, update_use_case, uow_mock, existing_user
    ):
        """
        GIVEN: Usuario existe y envío el mismo email que ya tiene
        WHEN: Ejecuto el use case
        THEN: NO se valida unicidad del email (no se llama exists_by_email)
        """
        # Arrange
        uow_mock.users.find_by_id.return_value = existing_user

        updated_user = User(
            id=1,
            name="Juan Pérez Actualizado",
            email="juan@example.com",  # Mismo email
            wage=Money(Decimal("50000.00"), Currency.ARS),
        )
        uow_mock.users.save.return_value = updated_user

        update_dto = UpdateUserInputDTO(
            id=1,
            name="Juan Pérez Actualizado",
            email="juan@example.com",  # Mismo email que el usuario existente
            wage_amount=None,
            wage_currency=None,
        )

        # Act
        result = update_use_case.execute(update_dto)

        # Assert - Verificar que NO se llamó a exists_by_email
        uow_mock.users.exists_by_email.assert_not_called()

        # Assert - Verificar que sí se guardó y commiteó
        uow_mock.users.save.assert_called_once()
        uow_mock.commit.assert_called_once()

        # Assert - Verificar resultado
        assert result.name == "Juan Pérez Actualizado"
        assert result.email == "juan@example.com"

    def test_raises_error_if_user_not_found(self, update_use_case, uow_mock):
        """
        GIVEN: Usuario con ID dado no existe
        WHEN: Intento actualizar usuario
        THEN: Lanza UserNotFoundError
        """
        # Arrange
        uow_mock.users.find_by_id.return_value = None  # Usuario no encontrado

        update_dto = UpdateUserInputDTO(
            id=999,
            name="Usuario Inexistente",
            email=None,
            wage_amount=None,
            wage_currency=None,
        )

        # Act & Assert
        with pytest.raises(UserNotFoundError) as exc_info:
            update_use_case.execute(update_dto)

        # Verificar mensaje de error
        assert "User with ID 999 not found" in str(exc_info.value)

        # Verificar que NO se guardó nada
        uow_mock.users.save.assert_not_called()
        uow_mock.commit.assert_not_called()

    def test_raises_error_if_email_already_exists(
        self, update_use_case, uow_mock, existing_user
    ):
        """
        GIVEN: Email nuevo ya existe en otro usuario
        WHEN: Intento actualizar email
        THEN: Lanza UserAlreadyExistsError y NO actualiza
        """
        # Arrange
        uow_mock.users.find_by_id.return_value = existing_user
        uow_mock.users.exists_by_email.return_value = True  # Email ya existe

        update_dto = UpdateUserInputDTO(
            id=1,
            name=None,
            email="existing@example.com",  # Email que ya existe
            wage_amount=None,
            wage_currency=None,
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            update_use_case.execute(update_dto)

        # Verificar mensaje de error
        assert "existing@example.com" in str(exc_info.value)

        # Verificar que NO se guardó nada
        uow_mock.users.save.assert_not_called()
        uow_mock.commit.assert_not_called()

    def test_no_fields_provided_raises_validation_error(self):
        """
        GIVEN: DTO sin campos para actualizar
        WHEN: Intento crear el DTO
        THEN: DTO validation falla con "Update has no fields to set"
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            UpdateUserInputDTO(
                id=1,
                name=None,
                email=None,
                wage_amount=None,
                wage_currency=None,
            )

        # Verificar mensaje de error
        assert "Update has no fields to set" in str(exc_info.value)
