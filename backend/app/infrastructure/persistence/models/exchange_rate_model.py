from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.infrastructure.persistence.models.base import Base


class ExchangeRateModel(Base):
    """SQLAlchemy model for exchange_rates table"""

    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    from_currency = Column(String(3), nullable=False, server_default="USD")
    to_currency = Column(String(3), nullable=False, server_default="ARS")
    rate = Column(Numeric(precision=12, scale=4), nullable=False)
    rate_type = Column(String(20), nullable=False)
    source = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ExchangeRateModel(id={self.id}, date={self.date}, rate={self.rate}, type={self.rate_type})>"
