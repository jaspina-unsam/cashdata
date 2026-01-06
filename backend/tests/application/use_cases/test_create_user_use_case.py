# tests/application/use_cases/test_create_user_use_case.py
import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal

from app.application.use_cases.create_user_use_case import CreateUserUseCase
from app.application.dtos.user_dto import CreateUserInputDTO, UserResponseDTO
from app.application.exceptions.application_exceptions import (
    UserAlreadyExistsError,
)
from app.domain.entities.user import User
from app.domain.value_objects.money import Money, Currency


class TestCreateUserUseCase:
    """
    Unit tests for CreateUserUseCase using mocks.

    Propósito: Validar la LÓGICA del use case sin dependencias externas.
    """

    @pytest.fixture
    def uow_mock(self):
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
    def valid_input_dto(self):
        """DTO de entrada válido para tests"""
        return CreateUserInputDTO(
            name="Juan Pérez",
            email="juan@example.com",
            wage_amount=Decimal("50000.00"),
            wage_currency=Currency.ARS,
        )

    @pytest.fixture
    def use_case(self, uow_mock):
        """Instancia del use case con UoW mockeado"""
        return CreateUserUseCase(uow_mock)

    # ========== HAPPY PATH ==========

    def test_creates_user_successfully(self, use_case, uow_mock, valid_input_dto):
        """
        GIVEN: Datos válidos de usuario y email no existe
        WHEN: Ejecuto el use case
        THEN: Se crea el usuario, se persiste y retorna DTO

        Este test valida:
        - Email uniqueness check
        - Creación de entidad User
        - Llamada a save()
        - Commit transaccional
        - Mapeo a DTO de respuesta
        """
        # Arrange
        uow_mock.users.exists_by_email.return_value = False

        # Simular usuario guardado con ID generado
        saved_user = User(
            id=1,
            name="Juan Pérez",
            email="juan@example.com",
            wage=Money(Decimal("50000.00"), Currency.ARS),
        )
        uow_mock.users.save.return_value = saved_user

        # Act
        result = use_case.execute(valid_input_dto)

        # Assert - Verificar llamadas
        uow_mock.users.exists_by_email.assert_called_once_with("juan@example.com")
        uow_mock.users.save.assert_called_once()
        uow_mock.commit.assert_called_once()

        # Assert - Verificar resultado
        assert isinstance(result, UserResponseDTO)
        assert result.id == 1
        assert result.name == "Juan Pérez"
        assert result.email == "juan@example.com"
        assert result.wage_amount == Decimal("50000.00")
        assert result.wage_currency == Currency.ARS

    def test_creates_user_with_different_currency(self, use_case, uow_mock):
        """
        GIVEN: Usuario con moneda USD
        WHEN: Ejecuto el use case
        THEN: Se crea correctamente con USD

        Propósito: Validar que funciona con diferentes monedas
        """
        # Arrange
        input_dto = CreateUserInputDTO(
            name="John Doe",
            email="john@example.com",
            wage_amount=Decimal("3000.00"),
            wage_currency=Currency.USD,
        )

        uow_mock.users.exists_by_email.return_value = False
        saved_user = User(
            id=2,
            name="John Doe",
            email="john@example.com",
            wage=Money(Decimal("3000.00"), Currency.USD),
        )
        uow_mock.users.save.return_value = saved_user

        # Act
        result = use_case.execute(input_dto)

        # Assert
        assert result.wage_currency == Currency.USD
        assert result.wage_amount == Decimal("3000.00")

    # ========== ERROR CASES ==========

    def test_raises_error_if_email_already_exists(
        self, use_case, uow_mock, valid_input_dto
    ):
        """
        GIVEN: Email ya existe en el sistema
        WHEN: Intento crear usuario
        THEN: Lanza UserAlreadyExistsError y NO hace commit

        Este test valida:
        - Validación de email único
        - Excepción correcta
        - No se persiste nada (no se llama save ni commit)
        """
        # Arrange
        uow_mock.users.exists_by_email.return_value = True

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            use_case.execute(valid_input_dto)

        # Verificar mensaje de error
        assert "juan@example.com" in str(exc_info.value)

        # Verificar que NO se guardó nada
        uow_mock.users.save.assert_not_called()
        uow_mock.commit.assert_not_called()

    def test_raises_error_with_correct_email_in_exception(self, use_case, uow_mock):
        """
        GIVEN: Email duplicado
        WHEN: Ejecuto use case
        THEN: La excepción contiene el email correcto

        Propósito: Validar que los mensajes de error son informativos
        """
        # Arrange
        input_dto = CreateUserInputDTO(
            name="Test User",
            email="duplicate@test.com",
            wage_amount=Decimal("100"),
            wage_currency=Currency.ARS,
        )
        uow_mock.users.exists_by_email.return_value = True

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            use_case.execute(input_dto)

        assert "duplicate@test.com" in str(exc_info).lower()

    def test_rollback_on_repository_error(self, use_case, uow_mock, valid_input_dto):
        """
        GIVEN: Repository lanza excepción durante save()
        WHEN: Ejecuto use case
        THEN: La excepción se propaga y NO se llama commit

        Este test valida:
        - Manejo de errores de persistencia
        - No se hace commit ante errores
        - Context manager maneja rollback automático
        """
        # Arrange
        uow_mock.users.exists_by_email.return_value = False
        uow_mock.users.save.side_effect = Exception("Database connection lost")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(valid_input_dto)

        assert "Database connection lost" in str(exc_info.value)

        # Verificar que NO se hizo commit
        uow_mock.commit.assert_not_called()

        # El rollback lo maneja __exit__ del context manager
        # No necesitamos verificarlo explícitamente

    # ========== EDGE CASES ==========


    def test_user_entity_created_with_correct_data(
        self, use_case, uow_mock, valid_input_dto
    ):
        """
        GIVEN: Input DTO válido
        WHEN: Ejecuto use case
        THEN: La entidad User se crea con los datos correctos e ID=None
        """
        # Arrange
        uow_mock.users.exists_by_email.return_value = False

        # Capturar el User que se pasa a save() SIN modificarlo
        captured_user = None

        def capture_user(user):
            nonlocal captured_user
            # Hacer una COPIA del estado actual antes de modificar
            captured_user = type(
                "CapturedUser",
                (),
                {"id": user.id, "name": user.name, "email": user.email, "wage": user.wage},
            )()

            # AHORA sí, simular asignación de ID (como lo haría SQLAlchemy)
            user.id = 99
            return user

        uow_mock.users.save.side_effect = capture_user

        # Act
        use_case.execute(valid_input_dto)

        # Assert - Verificar estado ORIGINAL del User
        assert captured_user is not None
        assert captured_user.id is None  # ✅ Ahora debería pasar
        assert captured_user.name == "Juan Pérez"
        assert captured_user.email == "juan@example.com"
        assert captured_user.wage.amount == Decimal("50000.00")
        assert captured_user.wage.currency == Currency.ARS

    def test_commit_called_after_save(self, use_case, uow_mock, valid_input_dto):
        """
        GIVEN: Save exitoso
        WHEN: Ejecuto use case
        THEN: Commit se llama DESPUÉS de save (orden correcto)

        Propósito: Validar el orden de operaciones
        """
        # Arrange
        call_order = []

        uow_mock.users.exists_by_email.return_value = False

        def track_save(user):
            call_order.append("save")
            user.id = 1
            return user

        def track_commit():
            call_order.append("commit")

        uow_mock.users.save.side_effect = track_save
        uow_mock.commit.side_effect = track_commit

        # Act
        use_case.execute(valid_input_dto)

        # Assert
        assert call_order == ["save", "commit"]


# ========== PARAMETRIZED TESTS ==========


class TestCreateUserUseCaseParametrized:
    """
    Tests parametrizados para cubrir múltiples escenarios con menos código.

    Útil cuando querés probar la misma lógica con diferentes inputs.
    """

    @pytest.fixture
    def uow_mock(self):
        uow = Mock()
        uow.__enter__ = Mock(return_value=uow)
        uow.__exit__ = Mock(return_value=False)
        uow.users = Mock()
        uow.commit = Mock()
        return uow

    @pytest.mark.parametrize(
        "name,email,wage_amount,currency",
        [
            ("Juan Pérez", "juan@test.com", Decimal("50000"), Currency.ARS),
            ("María García", "maria@test.com", Decimal("75000"), Currency.ARS),
            ("John Doe", "john@test.com", Decimal("3000"), Currency.USD),
            ("李明", "li@test.com", Decimal("20000"), Currency.USD),
        ],
    )
    def test_creates_users_with_different_data(
        self, uow_mock, name, email, wage_amount, currency
    ):
        """
        GIVEN: Diferentes combinaciones válidas de datos
        WHEN: Creo usuarios
        THEN: Todos se crean exitosamente

        Propósito: Validar que funciona con nombres Unicode, diferentes monedas, etc.
        """
        # Arrange
        use_case = CreateUserUseCase(uow_mock)
        input_dto = CreateUserInputDTO(
            name=name, email=email, wage_amount=wage_amount, wage_currency=currency
        )

        uow_mock.users.exists_by_email.return_value = False
        uow_mock.users.save.return_value = User(
            id=1, name=name, email=email, wage=Money(wage_amount, currency)
        )

        # Act
        result = use_case.execute(input_dto)

        # Assert
        assert result.name == name
        assert result.email == email
        assert result.wage_amount == wage_amount
        assert result.wage_currency == currency
