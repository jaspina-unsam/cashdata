from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.infrastructure.persistence.models.base import Base


class MonthlyBudgetModel(Base):
    """SQLAlchemy model for monthly_budgets table"""

    __tablename__ = "monthly_budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False)  # BudgetStatus enum value
    created_by_user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    # Relationships
    expenses = relationship("BudgetExpenseModel", back_populates="budget")
    participants = relationship("BudgetParticipantModel", back_populates="budget", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MonthlyBudgetModel(id={self.id}, name='{self.name}')>"