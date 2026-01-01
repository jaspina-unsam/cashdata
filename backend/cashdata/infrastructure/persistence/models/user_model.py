from sqlalchemy import Boolean, Column, DateTime, Integer, String, Numeric
from cashdata.infrastructure.persistence.models.base import Base

class UserModel(Base):
    """SQLAlchemy model for users table"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    wage_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    wage_currency = Column(String(3), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<UserModel(id={self.id}, name='{self.name}', email='{self.email}')>"
