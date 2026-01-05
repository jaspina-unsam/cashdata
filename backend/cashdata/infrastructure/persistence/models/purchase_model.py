from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from cashdata.infrastructure.persistence.models.base import Base


class PurchaseModel(Base):
    """SQLAlchemy model for purchases table"""

    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    credit_card_id = Column(Integer, ForeignKey("credit_cards.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    purchase_date = Column(Date, nullable=False)
    description = Column(String(200), nullable=False)
    total_amount = Column(Numeric(precision=12, scale=2), nullable=False)
    total_currency = Column(String(3), nullable=False)
    installments_count = Column(Integer, nullable=False)
    monthly_statement_id = Column(Integer, ForeignKey("monthly_statements.id"), nullable=True)

    def __repr__(self):
        return f"<PurchaseModel(id={self.id}, description='{self.description}', amount={self.total_amount})>"
