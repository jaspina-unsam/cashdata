from sqlalchemy import CheckConstraint, Column, Integer, Date, ForeignKey
from cashdata.infrastructure.persistence.models.base import Base


class MonthlyStatementModel(Base):
    """SQLAlchemy model for monthly_statements table"""

    __tablename__ = "monthly_statements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    credit_card_id = Column(Integer, ForeignKey("credit_cards.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    closing_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "start_date < closing_date AND closing_date <= due_date",
            name="ck_monthly_statements_dates_order",
        ),
    )

    def __repr__(self):
        return (
            f"<MonthlyStatementModel(id={self.id}, "
            f"credit_card_id={self.credit_card_id}, "
            f"start_date={self.start_date}, "
            f"closing_date={self.closing_date}, "
            f"due_date={self.due_date})>"
        )
