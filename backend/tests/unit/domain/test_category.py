import pytest
from dataclasses import FrozenInstanceError
from cashdata.domain.entities.category import Category


class TestCategoryEntity:
    """Unit tests for Category domain entity"""

    # ===== HAPPY PATH =====

    def test_create_category_with_all_fields(self):
        """
        GIVEN: Valid category data with all fields
        WHEN: Creating a Category
        THEN: Entity is created successfully
        """
        # Arrange & Act
        category = Category(id=1, name="Supermercado", color="#FF5733", icon="🛒")

        # Assert
        assert category.id == 1
        assert category.name == "Supermercado"
        assert category.color == "#FF5733"
        assert category.icon == "🛒"

    def test_create_category_with_minimal_fields(self):
        """
        GIVEN: Only required fields (name)
        WHEN: Creating a Category
        THEN: Optional fields default to None
        """
        # Arrange & Act
        category = Category(id=None, name="Transporte")

        # Assert
        assert category.id is None
        assert category.name == "Transporte"
        assert category.color is None
        assert category.icon is None

    def test_create_category_without_id(self):
        """
        GIVEN: Category data without ID (new entity)
        WHEN: Creating a Category
        THEN: ID should be None
        """
        # Arrange & Act
        category = Category(id=None, name="Salud")

        # Assert
        assert category.id is None
        assert category.name == "Salud"

    def test_strips_whitespace_from_name(self):
        """
        GIVEN: Category name with leading/trailing spaces
        WHEN: Creating a Category
        THEN: Name should be trimmed
        """
        # Arrange & Act
        category = Category(id=1, name="  Tecnología  ")

        # Assert
        assert category.name == "Tecnología"

    # ===== ERROR CASES =====

    def test_raises_error_for_empty_name(self):
        """
        GIVEN: Empty string as name
        WHEN: Creating a Category
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Category name cannot be empty"):
            Category(id=None, name="")

    def test_raises_error_for_whitespace_only_name(self):
        """
        GIVEN: Name with only spaces
        WHEN: Creating a Category
        THEN: Should raise ValueError
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Category name cannot be empty"):
            Category(id=None, name="   ")

    def test_raises_error_for_name_too_long(self):
        """
        GIVEN: Name longer than 50 characters
        WHEN: Creating a Category
        THEN: Should raise ValueError
        """
        # Arrange
        long_name = "A" * 51  # 51 characters

        # Act & Assert
        with pytest.raises(
            ValueError, match="Category name cannot exceed 50 characters"
        ):
            Category(id=None, name=long_name)

    # ===== EQUALITY =====

    def test_categories_equal_by_id(self):
        """
        GIVEN: Two categories with same ID
        WHEN: Comparing them
        THEN: They should be equal
        """
        # Arrange
        category1 = Category(id=1, name="Supermercado", color="#FF5733")
        category2 = Category(id=1, name="Otro Nombre", color="#000000")

        # Act & Assert
        assert category1 == category2

    def test_categories_not_equal_different_id(self):
        """
        GIVEN: Two categories with different IDs
        WHEN: Comparing them
        THEN: They should not be equal
        """
        # Arrange
        category1 = Category(id=1, name="Supermercado")
        category2 = Category(id=2, name="Supermercado")

        # Act & Assert
        assert category1 != category2

    def test_new_categories_not_equal(self):
        """
        GIVEN: Two new categories (id=None) with same name
        WHEN: Comparing them
        THEN: They should not be equal (different instances)
        """
        # Arrange
        category1 = Category(id=None, name="Supermercado")
        category2 = Category(id=None, name="Supermercado")

        # Act & Assert
        assert category1 != category2

    # ===== IMMUTABILITY =====

    def test_category_is_immutable(self):
        """
        GIVEN: A Category instance
        WHEN: Trying to modify a field
        THEN: Should raise FrozenInstanceError
        """
        # Arrange
        category = Category(id=1, name="Supermercado")

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            category.name = "Nuevo Nombre"


# ===== PARAMETRIZED TESTS =====


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "   ",
        "\t",
        "\n",
        "A" * 51,  # 51 characters
    ],
)
def test_invalid_names_raise_error(invalid_name):
    """Test various invalid name formats"""
    with pytest.raises(ValueError):
        Category(id=None, name=invalid_name)
