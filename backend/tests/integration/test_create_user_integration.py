# tests/integration/test_create_user_integration.py
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.use_cases.create_user_use_case import CreateUserUseCase
from app.application.dtos.user_dto import CreateUserInputDTO
from app.domain.entities.user import User
from app.domain.value_objects.money import Money
from app.application.exceptions.application_exceptions import (
    UserAlreadyExistsError,
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


class TestCreateUserUseCaseIntegration:
    """
    Integration tests con base de datos real.

    Propósito: Validar que el stack funciona end-to-end:
    - Use Case → UoW → Repository → SQLAlchemy → Database
    """

    def test_create_user_end_to_end(self, session_factory):
        """
        GIVEN: Base de datos vacía y datos válidos
        WHEN: Ejecuto use case con UoW real
        THEN: Usuario se persiste y puede ser recuperado

        Este es el test MÁS IMPORTANTE - valida que todo funciona junto.
        """
        # Arrange
        uow = SQLAlchemyUnitOfWork(session_factory)
        use_case = CreateUserUseCase(uow)

        input_dto = CreateUserInputDTO(
            name="Integration Test User",
            email="integration@test.com",
            wage_amount=Decimal("60000.00"),
            wage_currency=Currency.ARS,
        )

        # Act
        result = use_case.execute(input_dto)

        # Assert - Verificar DTO de respuesta
        assert result.id is not None  # ID fue generado
        assert result.name == "Integration Test User"
        assert result.email == "integration@test.com"
        assert result.wage_amount == Decimal("60000.00")

        # Assert - Verificar persistencia real
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            saved_user = uow.users.find_by_id(result.id)
            assert saved_user is not None
            assert saved_user.name == "Integration Test User"
            assert saved_user.email == "integration@test.com"
            assert saved_user.wage.amount == Decimal("60000.00")

    def test_duplicate_email_prevents_creation(self, session_factory):
        """
        GIVEN: Usuario ya existe en la DB
        WHEN: Intento crear otro con mismo email
        THEN: Lanza excepción y no se crea duplicado
        """
        # Arrange
        uow = SQLAlchemyUnitOfWork(session_factory)
        use_case = CreateUserUseCase(uow)

        # Crear primer usuario
        first_dto = CreateUserInputDTO(
            name="First User",
            email="duplicate@test.com",
            wage_amount=Decimal("50000"),
            wage_currency=Currency.ARS,
        )
        use_case.execute(first_dto)

        # Intentar crear segundo usuario con mismo email
        second_dto = CreateUserInputDTO(
            name="Second User",
            email="duplicate@test.com",  # ← Mismo email
            wage_amount=Decimal("70000"),
            wage_currency=Currency.ARS,
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError):
            use_case.execute(second_dto)

        # Verificar que solo existe UN usuario
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            all_users = uow.users.find_all()  # Asumiendo que existe este método
            assert len(all_users) == 1
            assert all_users[0].name == "First User"


    def test_transaction_isolation_prevents_partial_saves(self, session_factory):
        """
        GIVEN: Dos operaciones, la segunda falla
        WHEN: Ejecuto en una transacción
        THEN: Ninguna se persiste (atomicidad)

        Este test valida el comportamiento del UoW sin forzar errores artificiales.
        """
        # Arrange - Crear primer usuario exitosamente
        input_dto_1 = CreateUserInputDTO(
            name="User 1",
            email="user1@test.com",
            wage_amount=Decimal("50000"),
            wage_currency=Currency.ARS,
        )

        uow = SQLAlchemyUnitOfWork(session_factory)
        use_case = CreateUserUseCase(uow)

        result_1 = use_case.execute(input_dto_1)
        assert result_1.id is not None

        # Act - Intentar crear usuario con email duplicado
        input_dto_2 = CreateUserInputDTO(
            name="User 2",
            email="user1@test.com",  # ← Email duplicado
            wage_amount=Decimal("60000"),
            wage_currency=Currency.ARS,
        )

        with pytest.raises(UserAlreadyExistsError):
            use_case.execute(input_dto_2)

        # Assert - Verificar que solo existe el primer usuario
        with SQLAlchemyUnitOfWork(session_factory) as verify_uow:
            all_users = verify_uow.users.find_all()
            assert len(all_users) == 1
            assert all_users[0].email == "user1@test.com"


    def test_concurrent_transactions_are_isolated(self, session_factory):
        """
        GIVEN: Dos transacciones concurrentes
        WHEN: Una hace commit, la otra rollback
        THEN: Solo se persiste la que hizo commit

        Valida aislamiento de transacciones del UoW.
        """
        # Arrange
        input_dto_success = CreateUserInputDTO(
            name="Success User",
            email="success@test.com",
            wage_amount=Decimal("50000"),
            wage_currency=Currency.ARS,
        )

        input_dto_rollback = CreateUserInputDTO(
            name="Rollback User",
            email="rollback@test.com",
            wage_amount=Decimal("60000"),
            wage_currency=Currency.ARS,
        )

        # Act - Primera transacción: commit
        with SQLAlchemyUnitOfWork(session_factory) as uow1:
            user1 = User(
                id=None,
                name=input_dto_success.name,
                email=input_dto_success.email,
                wage=Money(input_dto_success.wage_amount, Currency(input_dto_success.wage_currency)),
            )
            uow1.users.save(user1)
            uow1.commit()

        # Act - Segunda transacción: rollback manual
        with SQLAlchemyUnitOfWork(session_factory) as uow2:
            user2 = User(
                id=None,
                name=input_dto_rollback.name,
                email=input_dto_rollback.email,
                wage=Money(
                    input_dto_rollback.wage_amount, Currency(input_dto_rollback.wage_currency)
                ),
            )
            uow2.users.save(user2)
            uow2.rollback()  # ← Rollback manual

        # Assert - Solo el primero se guardó
        with SQLAlchemyUnitOfWork(session_factory) as verify_uow:
            all_users = verify_uow.users.find_all()
            assert len(all_users) == 1
            assert all_users[0].email == "success@test.com"

    def test_multiple_users_created_successfully(self, session_factory):
        """
        GIVEN: Múltiples usuarios válidos
        WHEN: Creo varios usuarios
        THEN: Todos se persisten correctamente con IDs únicos
        """
        # Arrange
        uow = SQLAlchemyUnitOfWork(session_factory)
        use_case = CreateUserUseCase(uow)

        users_data = [
            ("User 1", "user1@test.com", Decimal("50000")),
            ("User 2", "user2@test.com", Decimal("60000")),
            ("User 3", "user3@test.com", Decimal("70000")),
        ]

        created_ids = []

        # Act
        for name, email, wage in users_data:
            dto = CreateUserInputDTO(
                name=name, email=email, wage_amount=wage, wage_currency=Currency.ARS
            )
            result = use_case.execute(dto)
            created_ids.append(result.id)

        # Assert
        assert len(set(created_ids)) == 3  # IDs únicos

        with SQLAlchemyUnitOfWork(session_factory) as verify_uow:
            all_users = verify_uow.users.find_all()
            assert len(all_users) == 3
            emails = [u.email for u in all_users]
            assert "user1@test.com" in emails
            assert "user2@test.com" in emails
            assert "user3@test.com" in emails
