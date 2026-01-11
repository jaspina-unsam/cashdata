from app.infrastructure.persistence.models.base import Base
from sqlalchemy import Column, ForeignKey, Integer, String


class BankAccountModel(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_method_id = Column(
        Integer, ForeignKey("payment_methods.id"), nullable=False
    )
    primary_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    secondary_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(100), nullable=False)
    bank = Column(String(100), nullable=False)
    account_type = Column(String(20), nullable=False, default="savings")
    last_four_digits = Column(String(4), nullable=False)
    currency = Column(String(3), nullable=False, default="ARS")

    def __repr__(self):
        return f"<BankAccountModel(id={self.id}, name='{self.name}', bank='{self.bank}', account_type='{self.account_type}')>"
