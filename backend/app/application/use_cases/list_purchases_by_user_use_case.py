from dataclasses import dataclass

from app.domain.entities.purchase import Purchase
from app.domain.repositories import IUnitOfWork


@dataclass(frozen=True)
class ListPurchasesByUserQuery:
    """Query to list all purchases for a user"""
    user_id: int


class ListPurchasesByUserUseCase:
    """
    Use case to list all purchases for a specific user.
    
    Returns all purchases ordered by purchase date (most recent first).
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work
    
    def execute(self, query: ListPurchasesByUserQuery) -> list[Purchase]:
        """
        Execute the use case to list purchases for a user.
        
        Args:
            query: The query containing user ID
            
        Returns:
            List of Purchase entities for the user
        """
        with self.unit_of_work as uow:
            purchases = uow.purchases.find_by_user_id(query.user_id)
            
            # Sort by purchase date descending (most recent first)
            return sorted(purchases, key=lambda p: p.purchase_date, reverse=True)
