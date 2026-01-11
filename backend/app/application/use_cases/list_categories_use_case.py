from app.domain.entities.category import Category
from app.domain.repositories.iunit_of_work import IUnitOfWork


class ListCategoriesUseCase:
    """
    Use case to list all categories.
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work
    
    def execute(self) -> list[Category]:
        """
        Execute the use case to list all categories.
        
        Returns:
            List of all Category entities
        """
        with self.unit_of_work as uow:
            return uow.categories.find_all()
