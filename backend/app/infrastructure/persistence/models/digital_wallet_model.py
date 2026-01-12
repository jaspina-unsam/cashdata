from app.infrastructure.persistence.models.base import Base
from sqlalchemy import Column, ForeignKey, Integer, String


class DigitalWalletModel(Base):
    __tablename__ = "digital_wallets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    provider = Column(String(100), nullable=False)
    identifier = Column(String(200), nullable=True)
    currency = Column(String(3), nullable=False)

    def __repr__(self):
        return f"<DigitalWalletModel(id={self.id}, provider='{self.provider}', name='{self.name}')>"
