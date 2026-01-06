from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.entities.purchase import Purchase
from app.domain.repositories.ipurchase_repository import IPurchaseRepository
from app.infrastructure.persistence.mappers.purchase_mapper import PurchaseMapper
from app.infrastructure.persistence.models.purchase_model import PurchaseModel


class SQLAlchemyPurchaseRepository(IPurchaseRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, purchase_id: int) -> Optional[Purchase]:
        """Retrieve purchase by ID"""
        purchase = self.session.scalars(
            select(PurchaseModel).where(PurchaseModel.id == purchase_id)
        ).first()
        return PurchaseMapper.to_entity(purchase) if purchase else None

    def find_by_user_id(self, user_id: int) -> List[Purchase]:
        """Retrieve all purchases for a specific user"""
        purchases = self.session.scalars(
            select(PurchaseModel).where(PurchaseModel.user_id == user_id)
        ).all()
        return [PurchaseMapper.to_entity(p) for p in purchases]

    def find_by_credit_card_id(self, card_id: int) -> List[Purchase]:
        """Retrieve all purchases for a specific credit card"""
        purchases = self.session.scalars(
            select(PurchaseModel).where(PurchaseModel.credit_card_id == card_id)
        ).all()
        return [PurchaseMapper.to_entity(p) for p in purchases]

    def save(self, purchase: Purchase) -> Purchase:
        """Insert or update purchase"""
        if purchase.id is not None:
            # Update existing
            existing = self.session.get(PurchaseModel, purchase.id)
            if existing:
                existing.user_id = purchase.user_id
                existing.credit_card_id = purchase.credit_card_id
                existing.category_id = purchase.category_id
                existing.purchase_date = purchase.purchase_date
                existing.description = purchase.description
                existing.total_amount = float(purchase.total_amount.amount)
                existing.total_currency = purchase.total_amount.currency.value
                existing.installments_count = purchase.installments_count
                self.session.flush()
                self.session.refresh(existing)
                return PurchaseMapper.to_entity(existing)

        # Insert new
        model = PurchaseMapper.to_model(purchase)
        merged_model = self.session.merge(model)
        self.session.flush()
        self.session.refresh(merged_model)
        return PurchaseMapper.to_entity(merged_model)
