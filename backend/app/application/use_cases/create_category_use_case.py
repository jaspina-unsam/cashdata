from dataclasses import dataclass

from app.domain.entities.category import Category
from app.domain.repositories import IUnitOfWork


@dataclass(frozen=True)
class CreateCategoryCommand:
    """Command to create a new category"""

    name: str
    color: str | None = None
    icon: str | None = None


class CreateCategoryUseCase:
    """
    Use case to create a new category.

    Categories are simple entities used to classify purchases.
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, command: CreateCategoryCommand) -> Category:
        """
        Execute the use case to create a category.

        Args:
            command: The command containing category data

        Returns:
            Created Category entity
        """
        with self.unit_of_work as uow:
            category = Category(
                id=None, name=command.name, color=command.color, icon=command.icon
            )

            saved_category = uow.categories.save(category)
            uow.commit()

            return saved_category
