from sqlalchemy import Boolean, Column, DateTime, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.infrastructure.persistence.models.base import Base

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

    # Relationships
    budget_expenses = relationship("BudgetExpenseModel", back_populates="paid_by_user")
    budget_expense_responsibilities = relationship("BudgetExpenseResponsibilityModel", back_populates="user")
    budget_participations = relationship("BudgetParticipantModel", back_populates="user")

    def __repr__(self):
        return f"<UserModel(id={self.id}, name='{self.name}', email='{self.email}')>"
