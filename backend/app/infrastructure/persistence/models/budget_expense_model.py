from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.persistence.models.base import Base


class BudgetExpenseModel(Base):
    __tablename__ = "budget_expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    budget_id = Column(Integer, ForeignKey("monthly_budgets.id"), nullable=False)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=True)
    installment_id = Column(Integer, ForeignKey("installments.id"), nullable=True)
    paid_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    split_type = Column(String(20), nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    currency = Column(String(3), server_default="ARS", nullable=False)
    description = Column(String(255), nullable=True)
    date = Column(Date, nullable=False)
    payment_method_name = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "split_type IN ('equal', 'proportional', 'custom', 'full_single')",
            name="ck_split_type_in_expected_list"
        ),
        CheckConstraint(
            "NOT (purchase_id IS NOT NULL AND installment_id IS NOT NULL)",
            name="ck_xor_purchase_installment"
        ),
        Index("idx_budget_expenses_budget", "budget_id"),
        Index("idx_budget_expenses_purchase", "purchase_id"),
        Index("idx_budget_expenses_installment", "installment_id"),
        Index("idx_budget_expenses_paid_by", "paid_by_user_id"),
    )

    # Relationships
    budget = relationship("MonthlyBudgetModel", back_populates="expenses")
    purchase = relationship("PurchaseModel", back_populates="budget_expenses")
    installment = relationship("InstallmentModel", back_populates="budget_expenses")
    paid_by_user = relationship("UserModel", back_populates="budget_expenses")
    responsibilities = relationship("BudgetExpenseResponsibilityModel", back_populates="budget_expense", cascade="all, delete-orphan")