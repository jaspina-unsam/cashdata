from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.repositories.idigital_wallet_repository import IDigitalWalletRepository
from app.domain.entities.digital_wallet import DigitalWallet
from app.infrastructure.persistence.models.digital_wallet_model import DigitalWalletModel
from app.infrastructure.persistence.mappers.digital_wallet_mapper import DigitalWalletMapper


class SQLAlchemyDigitalWalletRepository(IDigitalWalletRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_user_id(self, user_id: int) -> List[DigitalWallet]:
        rows = self.session.scalars(select(DigitalWalletModel).where(DigitalWalletModel.user_id == user_id)).all()
        return [DigitalWalletMapper.to_entity(r) for r in rows]

    def find_by_id(self, wallet_id: int) -> DigitalWallet | None:
        row = self.session.get(DigitalWalletModel, wallet_id)
        return DigitalWalletMapper.to_entity(row) if row else None

    def save(self, digital_wallet: DigitalWallet) -> DigitalWallet:
        if digital_wallet.id is not None:
            existing = self.session.get(DigitalWalletModel, digital_wallet.id)
            if existing:
                existing.name = digital_wallet.name
                existing.provider = digital_wallet.provider
                existing.identifier = digital_wallet.identifier
                existing.currency = digital_wallet.currency.value
                self.session.flush()
                self.session.refresh(existing)
                return DigitalWalletMapper.to_entity(existing)

        new_model = DigitalWalletModel(
            payment_method_id=digital_wallet.payment_method_id,
            user_id=digital_wallet.user_id,
            name=digital_wallet.name,
            provider=digital_wallet.provider,
            identifier=digital_wallet.identifier,
            currency=digital_wallet.currency.value,
        )
        self.session.add(new_model)
        self.session.flush()
        self.session.refresh(new_model)
        return DigitalWalletMapper.to_entity(new_model)

    def delete(self, digital_wallet: DigitalWallet) -> None:
        existing = self.session.get(DigitalWalletModel, digital_wallet.id)
        if existing:
            self.session.delete(existing)
            self.session.flush()

    def exists_by_payment_method_id(self, payment_method_id: int) -> bool:
        exists = self.session.scalars(select(DigitalWalletModel).where(DigitalWalletModel.payment_method_id == payment_method_id)).first()
        return exists is not None
