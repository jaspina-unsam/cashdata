from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.entities.credit_card import CreditCard
from app.domain.repositories.icredit_card_repository import ICreditCardRepository
from app.infrastructure.persistence.mappers.credit_card_mapper import (
    CreditCardMapper,
)
from app.infrastructure.persistence.models.credit_card_model import CreditCardModel


class SQLAlchemyCreditCardRepository(ICreditCardRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, card_id: int) -> Optional[CreditCard]:
        """Retrieve credit card by ID"""
        card = self.session.scalars(
            select(CreditCardModel).where(CreditCardModel.id == card_id)
        ).first()
        return CreditCardMapper.to_entity(card) if card else None

    def find_by_user_id(self, user_id: int) -> List[CreditCard]:
        """Retrieve all credit cards for a specific user"""
        cards = self.session.scalars(
            select(CreditCardModel).where(CreditCardModel.user_id == user_id)
        ).all()
        return [CreditCardMapper.to_entity(c) for c in cards]

    def find_by_payment_method_id(self, payment_method_id: int) -> Optional[CreditCard]:
        """Retrieve credit card by payment method ID"""
        card = self.session.scalars(
            select(CreditCardModel).where(CreditCardModel.payment_method_id == payment_method_id)
        ).first()
        return CreditCardMapper.to_entity(card) if card else None

    def save(self, card: CreditCard) -> CreditCard:
        """Insert or update credit card"""
        if card.id is not None:
            # Update existing
            existing = self.session.get(CreditCardModel, card.id)
            if existing:
                existing.user_id = card.user_id
                existing.name = card.name
                existing.bank = card.bank
                existing.last_four_digits = card.last_four_digits
                existing.billing_close_day = card.billing_close_day
                existing.payment_due_day = card.payment_due_day
                if card.credit_limit is not None:
                    existing.credit_limit_amount = float(card.credit_limit.amount)
                    existing.credit_limit_currency = card.credit_limit.currency.value
                else:
                    existing.credit_limit_amount = None
                    existing.credit_limit_currency = None
                self.session.flush()
                self.session.refresh(existing)
                return CreditCardMapper.to_entity(existing)

        # Insert new
        model = CreditCardMapper.to_model(card)
        merged_model = self.session.merge(model)
        self.session.flush()
        self.session.refresh(merged_model)
        return CreditCardMapper.to_entity(merged_model)
