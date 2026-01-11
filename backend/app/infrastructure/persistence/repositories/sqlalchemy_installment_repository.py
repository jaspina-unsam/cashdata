from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.entities.installment import Installment
from app.domain.repositories.iinstallment_repository import IInstallmentRepository
from app.infrastructure.persistence.mappers.installment_mapper import (
    InstallmentMapper,
)
from app.infrastructure.persistence.models.installment_model import (
    InstallmentModel,
)
from app.infrastructure.persistence.models.purchase_model import PurchaseModel


class SQLAlchemyInstallmentRepository(IInstallmentRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, installment_id: int) -> Optional[Installment]:
        """Retrieve installment by ID"""
        installment = self.session.scalars(
            select(InstallmentModel).where(InstallmentModel.id == installment_id)
        ).first()
        return InstallmentMapper.to_entity(installment) if installment else None

    def find_by_purchase_id(self, purchase_id: int) -> List[Installment]:
        """Retrieve all installments for a specific purchase"""
        installments = self.session.scalars(
            select(InstallmentModel).where(
                InstallmentModel.purchase_id == purchase_id
            )
        ).all()
        return [InstallmentMapper.to_entity(i) for i in installments]

    def find_by_billing_period(self, period: str) -> List[Installment]:
        """Retrieve all installments for a specific billing period (YYYYMM)"""
        installments = self.session.scalars(
            select(InstallmentModel).where(InstallmentModel.billing_period == period)
        ).all()
        return [InstallmentMapper.to_entity(i) for i in installments]

    def find_by_credit_card_and_period(
        self, card_id: int, period: str
    ) -> List[Installment]:
        """Retrieve installments for a credit card in a specific period"""
        # Join with purchases to filter by payment_method_id
        installments = self.session.scalars(
            select(InstallmentModel)
            .join(PurchaseModel, InstallmentModel.purchase_id == PurchaseModel.id)
            .where(
                PurchaseModel.payment_method_id == card_id,
                InstallmentModel.billing_period == period,
            )
        ).all()
        return [InstallmentMapper.to_entity(i) for i in installments]

    def save(self, installment: Installment) -> Installment:
        """Insert or update installment"""
        if installment.id is not None:
            # Update existing
            existing = self.session.get(InstallmentModel, installment.id)
            if existing:
                existing.purchase_id = installment.purchase_id
                existing.installment_number = installment.installment_number
                existing.total_installments = installment.total_installments
                existing.amount = float(installment.amount.amount)
                existing.currency = installment.amount.currency.value
                existing.billing_period = installment.billing_period
                existing.manually_assigned_statement_id = installment.manually_assigned_statement_id
                self.session.flush()
                self.session.refresh(existing)
                return InstallmentMapper.to_entity(existing)

        # Insert new
        model = InstallmentMapper.to_model(installment)
        merged_model = self.session.merge(model)
        self.session.flush()
        self.session.refresh(merged_model)
        return InstallmentMapper.to_entity(merged_model)

    def save_all(self, installments: List[Installment]) -> List[Installment]:
        """Insert or update multiple installments (bulk operation)"""
        saved_installments = []
        for installment in installments:
            saved = self.save(installment)
            saved_installments.append(saved)
        return saved_installments

    def delete(self, installment_id: int) -> bool:
        """Delete installment by ID. Returns True if deleted, False if not found"""
        installment = self.session.get(InstallmentModel, installment_id)
        if installment:
            self.session.delete(installment)
            self.session.flush()
            return True
        return False
