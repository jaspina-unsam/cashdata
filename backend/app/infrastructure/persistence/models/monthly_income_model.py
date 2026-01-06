from sqlalchemy import Column, Integer, String, Numeric, UniqueConstraint
from app.infrastructure.persistence.models.base import Base


class MonthlyIncomeModel(Base):
    """SQLAlchemy model for monthly income table"""

    __tablename__ = "monthly_income"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=False)
    amount_value = Column(Numeric(10, 2), nullable=False)
    amount_currency = Column(String(3), nullable=False)
    source = Column(String(20), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "period_year", "period_month"),)

    def __repr__(self):
        return f"<MonthlyIncomeModel(id={self.id}, user_id='{self.user_id}', period='{self.period_month}-{self.period_year}', amount='{self.amount_value} {self.amount_currency}', source='{self.source}')>"
