from app.infrastructure.persistence.models.base import Base
from sqlalchemy import Column, ForeignKey, Integer, String


class CashAccountModel(Base):
    __tablename__ = "cash_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    currency = Column(String(3), nullable=False)

    def __repr__(self):
        return f"<CashAccountModel(id={self.id}, name='{self.name}', currency='{self.currency}')>"