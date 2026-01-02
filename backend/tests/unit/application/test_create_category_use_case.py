import pytest
from unittest.mock import Mock

from cashdata.application.use_cases.create_category_use_case import (
    CreateCategoryUseCase,
    CreateCategoryCommand,
)
from cashdata.domain.entities.category import Category


@pytest.fixture
def mock_unit_of_work():
    uow = Mock()
    uow.categories = Mock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


class TestCreateCategoryUseCase:
    
    def test_should_create_category_with_all_fields(self, mock_unit_of_work):
        """
        GIVEN: Valid category command with all fields
        WHEN: Execute use case
        THEN: Category is created and saved
        """
        # Arrange
        saved_category = Category(
            id=1,
            name="Electronics",
            color="#FF5733",
            icon="laptop"
        )
        mock_unit_of_work.categories.save.return_value = saved_category
        
        command = CreateCategoryCommand(
            name="Electronics",
            color="#FF5733",
            icon="laptop"
        )
        use_case = CreateCategoryUseCase(mock_unit_of_work)
        
        # Act
        result = use_case.execute(command)
        
        # Assert
        assert result.id == 1
        assert result.name == "Electronics"
        assert result.color == "#FF5733"
        assert result.icon == "laptop"
        mock_unit_of_work.categories.save.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()
    
    def test_should_create_category_with_minimal_fields(self, mock_unit_of_work):
        """
        GIVEN: Category command with only required field (name)
        WHEN: Execute use case
        THEN: Category is created with None for optional fields
        """
        # Arrange
        saved_category = Category(id=1, name="Food", color=None, icon=None)
        mock_unit_of_work.categories.save.return_value = saved_category
        
        command = CreateCategoryCommand(name="Food")
        use_case = CreateCategoryUseCase(mock_unit_of_work)
        
        # Act
        result = use_case.execute(command)
        
        # Assert
        assert result.name == "Food"
        assert result.color is None
        assert result.icon is None
