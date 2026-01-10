from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from app.infrastructure.persistence.models.base import Base


class PaymentMethodModel(Base):
    """SQLAlchemy model for payment_methods table"""

    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<PaymentMethodModel(id={self.id}, name='{self.name}', type='{self.type}')>"