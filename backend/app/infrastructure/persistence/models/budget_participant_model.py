from sqlalchemy import Column, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.infrastructure.persistence.models.base import Base


class BudgetParticipantModel(Base):
    __tablename__ = "budget_participants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    budget_id = Column(Integer, ForeignKey("monthly_budgets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Constraints and indexes
    __table_args__ = (
        Index("idx_budget_participants_budget", "budget_id"),
        Index("idx_budget_participants_user", "user_id"),
        Index("uk_budget_participants_unique", "budget_id", "user_id", unique=True),
    )

    # Relationships
    budget = relationship("MonthlyBudgetModel", back_populates="participants")
    user = relationship("UserModel", back_populates="budget_participations")