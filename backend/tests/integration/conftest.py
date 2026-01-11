import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.api.main import app
from app.infrastructure.api.dependencies import get_session
from app.domain.entities.user import User
from app.domain.value_objects.money import Money, Currency
from app.infrastructure.persistence.mappers.user_mapper import UserMapper

# Import Base and ALL models to ensure they're registered
from app.infrastructure.persistence.models import (
    Base,
    UserModel,
    MonthlyIncomeModel,
    CategoryModel,
    CreditCardModel,
    PaymentMethodModel,  # noqa: F401
    PurchaseModel,
    InstallmentModel,
)


@pytest.fixture
def db_engine():
    """Create in-memory SQLite engine for tests"""
    # Use shared cache mode so all connections see the same data
    engine = create_engine(
        "sqlite:///file:testdb?mode=memory&cache=shared&uri=true",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """Create database session for tests"""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    """Create FastAPI test client with test database"""

    def override_get_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user directly in database"""
    user = User(
        id=None,
        name="Test User",
        email="test@example.com",
        wage=Money(50000, Currency.ARS),
    )
    user_model = UserMapper.to_model(user)
    db_session.add(user_model)
    db_session.commit()
    db_session.refresh(user_model)
    return {"id": user_model.id, "name": user_model.name, "email": user_model.email}
