from dataclasses import dataclass
from typing import Optional

from cashdata.domain.entities.category import Category
from cashdata.domain.repositories import IUnitOfWork


@dataclass(frozen=True)
class GetCategoryByIdQuery:
    """Query to get a category by ID"""

    category_id: int


class GetCategoryByIdUseCase:
    """
    Use case to retrieve a category by its ID.
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: GetCategoryByIdQuery) -> Optional[Category]:
        """
        Execute the use case to get a category by ID.

        Args:
            query: The query containing category ID

        Returns:
            Category entity if found, None otherwise
        """
        with self.unit_of_work as uow:
            return uow.categories.find_by_id(query.category_id)
