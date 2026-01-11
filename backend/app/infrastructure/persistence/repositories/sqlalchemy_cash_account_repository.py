from typing import List
from app.infrastructure.persistence.mappers.cash_account_mapper import CashAccountMapper
from app.infrastructure.persistence.models.cash_account_model import CashAccountModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.repositories.icash_account_repository import ICashAccountRepository
from app.domain.entities.cash_account import CashAccount


class SQLAlchemyCashAccountRepository(ICashAccountRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_user_id(self, user_id: int) -> List[CashAccount]:
        cash = self.session.scalars(
            select(CashAccountModel).where(CashAccountModel.user_id == user_id)
        ).all()
        return [CashAccountMapper.to_entity(c) for c in cash]

    def find_by_id(self, account_id: int) -> CashAccount | None:
        cash = self.session.scalars(
            select(CashAccountModel).where(CashAccountModel.id == account_id)
        ).first()
        return CashAccountMapper.to_entity(cash) if cash else None

    def save(self, cash_account: CashAccount) -> CashAccount:
        """Insert or update cash account"""
        if cash_account.id is not None:
            # Update existing
            existing = self.session.get(CashAccountModel, cash_account.id)
            if existing:
                existing.user_id = cash_account.user_id
                existing.name = cash_account.name
                existing.currency = cash_account.currency.value
                self.session.flush()
                self.session.refresh(existing)
                return CashAccountMapper.to_entity(existing)

        # Insert new
        new_model = CashAccountModel(
            payment_method_id=cash_account.payment_method_id,
            user_id=cash_account.user_id,
            name=cash_account.name,
            currency=cash_account.currency.value,
        )
        self.session.add(new_model)
        self.session.flush()
        self.session.refresh(new_model)
        return CashAccountMapper.to_entity(new_model)

    def delete(self, cash_account: CashAccount) -> None:
        """Delete cash account"""
        existing = self.session.get(CashAccountModel, cash_account.id)
        if existing:
            self.session.delete(existing)
            self.session.flush()

    def exists_by_payment_method_id(self, payment_method_id: int) -> bool:
        """Check if a cash account exists for the given payment method ID"""
        exists = self.session.scalars(
            select(CashAccountModel).where(
                CashAccountModel.payment_method_id == payment_method_id
            )
        ).first()
        return exists is not None

    def find_all(self) -> List[CashAccount]:
        """Retrieve all cash accounts"""
        cash_accounts = self.session.scalars(select(CashAccountModel)).all()
        return [CashAccountMapper.to_entity(c) for c in cash_accounts]

    def exists_by_user_id_and_currency(self, user_id: int, currency: str) -> bool:
        """Check if a cash account exists for the given user and currency"""
        exists = self.session.scalars(
            select(CashAccountModel).where(
                CashAccountModel.user_id == user_id,
                CashAccountModel.currency == currency
            )
        ).first()
        return exists is not None
