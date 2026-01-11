from typing import List, Optional
from app.domain.entities.bank_account import BankAccount
from app.domain.repositories.ibank_account_repository import IBankAccountRepository
from app.infrastructure.persistence.mappers.bank_account_mapper import BankAccountMapper
from app.infrastructure.persistence.models.bank_account_model import BankAccountModel
from sqlalchemy.orm import Session
from sqlalchemy import select


class SQLAlchemyBankAccountRepository(IBankAccountRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_user_id(self, user_id: int) -> List[BankAccount]:
        accounts = self.session.scalars(
            select(BankAccountModel).where(
                (BankAccountModel.primary_user_id == user_id)
                | (BankAccountModel.secondary_user_id == user_id)
            )
        ).all()
        return [BankAccountMapper.to_entity(a) for a in accounts]

    def save(self, bank_account: BankAccount) -> BankAccount:
        """Insert or update bank account"""
        if bank_account.id is not None:
            # Update existing
            existing = self.session.get(BankAccountModel, bank_account.id)
            if existing:
                existing.primary_user_id = bank_account.primary_user_id
                existing.secondary_user_id = bank_account.secondary_user_id
                existing.name = bank_account.name
                existing.bank = bank_account.bank
                existing.account_type = bank_account.account_type
                existing.last_four_digits = bank_account.last_four_digits
                existing.currency = bank_account.currency.value
                self.session.flush()
                self.session.refresh(existing)
                return BankAccountMapper.to_entity(existing)

        # Insert new
        new_model = BankAccountModel(
            payment_method_id=bank_account.payment_method_id,
            primary_user_id=bank_account.primary_user_id,
            secondary_user_id=bank_account.secondary_user_id,
            name=bank_account.name,
            bank=bank_account.bank,
            account_type=bank_account.account_type,
            last_four_digits=bank_account.last_four_digits,
            currency=bank_account.currency.value,
        )
        self.session.add(new_model)
        self.session.flush()
        self.session.refresh(new_model)
        return BankAccountMapper.to_entity(new_model)

    def delete(self, bank_account: BankAccount) -> None:
        """Delete bank account"""
        existing = self.session.get(BankAccountModel, bank_account.id)
        if existing:
            self.session.delete(existing)
            self.session.flush()

    def find_by_id(self, account_id: int) -> Optional[BankAccount]:
        account = self.session.scalars(
            select(BankAccountModel).where(BankAccountModel.id == account_id)
        ).first()
        return BankAccountMapper.to_entity(account) if account else None

    def find_all(self) -> List[BankAccount]:
        accounts = self.session.scalars(select(BankAccountModel)).all()
        return [BankAccountMapper.to_entity(a) for a in accounts]
