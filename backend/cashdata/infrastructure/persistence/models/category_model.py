from sqlalchemy import Column, Integer, String
from cashdata.infrastructure.persistence.models.base import Base


class CategoryModel(Base):
    """SQLAlchemy model for categories table"""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    color = Column(String(7), nullable=True)  # Hex color like "#FF5733"
    icon = Column(String(10), nullable=True)  # Emoji like "🛒"

    def __repr__(self):
        return f"<CategoryModel(id={self.id}, name='{self.name}')>"
