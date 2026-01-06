from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.persistence.database import SessionLocal
from app.infrastructure.persistence.repositories.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
from app.domain.repositories import IUnitOfWork


def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_unit_of_work(session: Session = Depends(get_session)) -> IUnitOfWork:
    """Get UnitOfWork with session dependency"""
    def session_factory():
        return session
    return SQLAlchemyUnitOfWork(session_factory)
