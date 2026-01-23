from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.persistence.models.base import Base


class InstallmentModel(Base):
    """SQLAlchemy model for installments table"""

    __tablename__ = "installments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False)
    installment_number = Column(Integer, nullable=False)
    total_installments = Column(Integer, nullable=False)
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    currency = Column(String(3), nullable=False)
    billing_period = Column(String(6), nullable=False)
    manually_assigned_statement_id = Column(Integer, ForeignKey("monthly_statements.id"))
    
    # Dual-currency support
    original_currency = Column(String(3), nullable=True)
    original_amount = Column(Numeric(precision=12, scale=2), nullable=True)
    exchange_rate_id = Column(Integer, ForeignKey("exchange_rates.id"), nullable=True)


    # Relationships
    budget_expenses = relationship("BudgetExpenseModel", back_populates="installment")

    def __repr__(self):
        return f"<InstallmentModel(id={self.id}, purchase_id={self.purchase_id}, {self.installment_number}/{self.total_installments})>"
