from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from app.infrastructure.persistence.models.base import Base


class CreditCardModel(Base):
    """SQLAlchemy model for credit_cards table"""

    __tablename__ = "credit_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    bank = Column(String(100), nullable=False)
    last_four_digits = Column(String(4), nullable=False)
    billing_close_day = Column(Integer, nullable=False)
    payment_due_day = Column(Integer, nullable=False)
    credit_limit_amount = Column(Numeric(precision=12, scale=2), nullable=True)
    credit_limit_currency = Column(String(3), nullable=True)

    def __repr__(self):
        return f"<CreditCardModel(id={self.id}, name='{self.name}', bank='{self.bank}')>"
