from abc import ABC, abstractmethod
from typing import List, Optional

from cashdata.domain.entities.category import Category


class ICategoryRepository(ABC):
    @abstractmethod
    def find_by_id(self, category_id: int) -> Optional[Category]:
        """Retrieve category by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[Category]:
        """Retrieve all categories"""
        pass

    @abstractmethod
    def save(self, category: Category) -> Category:
        """Insert or update category"""
        pass
