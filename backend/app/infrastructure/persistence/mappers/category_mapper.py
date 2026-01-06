from app.domain.entities.category import Category
from app.infrastructure.persistence.models.category_model import CategoryModel


class CategoryMapper:
    @staticmethod
    def to_entity(model: CategoryModel) -> Category:
        """SQLAlchemy Model → Domain Entity"""
        return Category(
            id=model.id,
            name=model.name,
            color=model.color,
            icon=model.icon,
        )

    @staticmethod
    def to_model(entity: Category) -> CategoryModel:
        """Domain Entity → SQLAlchemy Model"""
        return CategoryModel(
            id=entity.id,
            name=entity.name,
            color=entity.color,
            icon=entity.icon,
        )
