import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cashdata.infrastructure.persistence.models.user_model import Base


@pytest.fixture
def db_session():
    """In-memory SQLite for tests"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
