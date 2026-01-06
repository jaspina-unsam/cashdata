from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator


DATABASE_URL = "sqlite:///./cashdata.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
