from sqlalchemy import Column, Integer, Numeric, String, CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.infrastructure.persistence.models.base import Base


class BudgetExpenseResponsibilityModel(Base):
    __tablename__ = "budget_expense_responsibilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    budget_expense_id = Column(Integer, ForeignKey("budget_expenses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    percentage = Column(Numeric(precision=5, scale=2), nullable=False)
    responsible_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    responsible_currency = Column(String(3), server_default="ARS", nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "percentage >= 0 AND percentage <= 100",
            name="ck_percentage_range"
        ),
        CheckConstraint(
            "responsible_amount >= 0",
            name="ck_responsible_amount_positive"
        ),
        Index("idx_budget_expense_responsibilities_budget_expense", "budget_expense_id"),
        Index("idx_budget_expense_responsibilities_user", "user_id"),
        Index("uk_budget_expense_responsibilities_unique", "budget_expense_id", "user_id", unique=True),
    )

    # Relationships
    budget_expense = relationship("BudgetExpenseModel", back_populates="responsibilities")
    user = relationship("UserModel", back_populates="budget_expense_responsibilities")