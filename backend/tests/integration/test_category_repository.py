import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.domain.entities.category import Category
from app.infrastructure.persistence.models.category_model import CategoryModel
from app.infrastructure.persistence.repositories.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)


@pytest.fixture
def db_session():
    """In-memory SQLite for tests"""
    engine = create_engine("sqlite:///:memory:")
    CategoryModel.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def category_repository(db_session: Session):
    return SQLAlchemyCategoryRepository(db_session)


class TestSQLAlchemyCategoryRepositorySave:
    def test_should_save_new_category(self, category_repository):
        # Arrange
        new_category = Category(id=None, name="Groceries", color="#FF5733", icon="🛒")

        # Act
        saved_category = category_repository.save(new_category)

        # Assert
        assert saved_category.id is not None
        assert saved_category.name == "Groceries"
        assert saved_category.color == "#FF5733"
        assert saved_category.icon == "🛒"

        # Verify in DB
        retrieved = category_repository.find_by_id(saved_category.id)
        assert retrieved == saved_category

    def test_should_save_category_with_minimal_fields(self, category_repository):
        # Arrange
        new_category = Category(id=None, name="Transport")

        # Act
        saved_category = category_repository.save(new_category)

        # Assert
        assert saved_category.id is not None
        assert saved_category.name == "Transport"
        assert saved_category.color is None
        assert saved_category.icon is None

    def test_should_update_existing_category(self, category_repository):
        # Arrange - Create and save
        category = Category(id=None, name="Food", color="#FF0000", icon="🍕")
        saved = category_repository.save(category)
        original_id = saved.id

        # Act - Update
        updated_category = Category(
            id=original_id, name="Food & Drinks", color="#00FF00", icon="🍔"
        )
        updated = category_repository.save(updated_category)

        # Assert
        assert updated.id == original_id
        assert updated.name == "Food & Drinks"
        assert updated.color == "#00FF00"
        assert updated.icon == "🍔"

        # Verify in DB
        from_db = category_repository.find_by_id(original_id)
        assert from_db.name == "Food & Drinks"


class TestSQLAlchemyCategoryRepositoryFindById:
    def test_should_find_existing_category(self, category_repository):
        # Arrange
        category = Category(id=None, name="Entertainment", icon="🎬")
        saved = category_repository.save(category)

        # Act
        found = category_repository.find_by_id(saved.id)

        # Assert
        assert found is not None
        assert found.id == saved.id
        assert found.name == "Entertainment"

    def test_should_return_none_for_nonexistent_id(self, category_repository):
        # Act
        found = category_repository.find_by_id(999)

        # Assert
        assert found is None


class TestSQLAlchemyCategoryRepositoryFindAll:
    def test_should_return_all_categories(self, category_repository):
        # Arrange
        cat1 = Category(id=None, name="Category 1")
        cat2 = Category(id=None, name="Category 2")
        cat3 = Category(id=None, name="Category 3")

        category_repository.save(cat1)
        category_repository.save(cat2)
        category_repository.save(cat3)

        # Act
        all_categories = category_repository.find_all()

        # Assert
        assert len(all_categories) == 3
        names = [c.name for c in all_categories]
        assert "Category 1" in names
        assert "Category 2" in names
        assert "Category 3" in names

    def test_should_return_empty_list_when_no_categories(self, category_repository):
        # Act
        all_categories = category_repository.find_all()

        # Assert
        assert all_categories == []
