from sqlalchemy import Column, Integer, Date, ForeignKey
from cashdata.infrastructure.persistence.models.base import Base


class MonthlyStatementModel(Base):
    """SQLAlchemy model for monthly_statements table"""

    __tablename__ = "monthly_statements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    credit_card_id = Column(Integer, ForeignKey("credit_cards.id"), nullable=False)
    billing_close_date = Column(Date, nullable=False)
    payment_due_date = Column(Date, nullable=False)

    def __repr__(self):
        return (
            f"<MonthlyStatementModel(id={self.id}, "
            f"credit_card_id={self.credit_card_id}, "
            f"billing_close_date={self.billing_close_date}, "
            f"payment_due_date={self.payment_due_date})>"
        )
