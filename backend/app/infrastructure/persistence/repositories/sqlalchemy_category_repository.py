from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.entities.category import Category
from app.domain.repositories.icategory_repository import ICategoryRepository
from app.infrastructure.persistence.mappers.category_mapper import CategoryMapper
from app.infrastructure.persistence.models.category_model import CategoryModel


class SQLAlchemyCategoryRepository(ICategoryRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, category_id: int) -> Optional[Category]:
        """Retrieve category by ID"""
        category = self.session.scalars(
            select(CategoryModel).where(CategoryModel.id == category_id)
        ).first()
        return CategoryMapper.to_entity(category) if category else None

    def find_all(self) -> List[Category]:
        """Retrieve all categories"""
        categories = self.session.scalars(select(CategoryModel)).all()
        return [CategoryMapper.to_entity(c) for c in categories]

    def save(self, category: Category) -> Category:
        """Insert or update category"""
        if category.id is not None:
            # Update existing
            existing = self.session.get(CategoryModel, category.id)
            if existing:
                existing.name = category.name
                existing.color = category.color
                existing.icon = category.icon
                self.session.flush()
                self.session.refresh(existing)
                return CategoryMapper.to_entity(existing)

        # Insert new
        model = CategoryMapper.to_model(category)
        merged_model = self.session.merge(model)
        self.session.flush()
        self.session.refresh(merged_model)
        return CategoryMapper.to_entity(merged_model)
