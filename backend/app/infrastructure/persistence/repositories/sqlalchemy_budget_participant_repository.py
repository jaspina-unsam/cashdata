from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, and_

from app.domain.entities.budget_participant import BudgetParticipant
from app.domain.repositories.ibudget_participant_repository import IBudgetParticipantRepository
from app.infrastructure.persistence.mappers.budget_participant_mapper import BudgetParticipantMapper
from app.infrastructure.persistence.models.budget_participant_model import BudgetParticipantModel


class SQLAlchemyBudgetParticipantRepository(IBudgetParticipantRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, participant_id: int) -> Optional[BudgetParticipant]:
        """Retrieve budget participant by ID"""
        participant = self.session.scalars(
            select(BudgetParticipantModel).where(BudgetParticipantModel.id == participant_id)
        ).first()
        return BudgetParticipantMapper.to_entity(participant) if participant else None

    def find_by_budget_id(self, budget_id: int) -> List[BudgetParticipant]:
        """Find all participants for a specific budget"""
        participants = self.session.scalars(
            select(BudgetParticipantModel).where(BudgetParticipantModel.budget_id == budget_id)
        ).all()
        return [BudgetParticipantMapper.to_entity(p) for p in participants]

    def find_by_user_id(self, user_id: int) -> List[BudgetParticipant]:
        """Find all budgets where a user is a participant"""
        participants = self.session.scalars(
            select(BudgetParticipantModel).where(BudgetParticipantModel.user_id == user_id)
        ).all()
        return [BudgetParticipantMapper.to_entity(p) for p in participants]

    def find_by_budget_and_user(self, budget_id: int, user_id: int) -> Optional[BudgetParticipant]:
        """Find a specific participant relationship"""
        participant = self.session.scalars(
            select(BudgetParticipantModel).where(
                and_(
                    BudgetParticipantModel.budget_id == budget_id,
                    BudgetParticipantModel.user_id == user_id
                )
            )
        ).first()
        return BudgetParticipantMapper.to_entity(participant) if participant else None

    def save(self, participant: BudgetParticipant) -> BudgetParticipant:
        """Insert or update budget participant"""
        if participant.id is not None:
            # Update existing
            existing = self.session.get(BudgetParticipantModel, participant.id)
            if existing:
                existing.budget_id = participant.budget_id
                existing.user_id = participant.user_id
                self.session.flush()
                self.session.refresh(existing)
                return BudgetParticipantMapper.to_entity(existing)

        # Insert new
        model = BudgetParticipantMapper.to_model(participant)
        merged_model = self.session.merge(model)
        self.session.flush()
        self.session.refresh(merged_model)
        return BudgetParticipantMapper.to_entity(merged_model)

    def save_many(self, participants: List[BudgetParticipant]) -> List[BudgetParticipant]:
        """Insert or update multiple budget participants"""
        result = []
        for participant in participants:
            saved = self.save(participant)
            result.append(saved)
        return result

    def delete(self, participant_id: int) -> None:
        """Delete budget participant by ID"""
        self.session.execute(
            delete(BudgetParticipantModel).where(BudgetParticipantModel.id == participant_id)
        )

    def delete_by_budget_id(self, budget_id: int) -> None:
        """Delete all participants for a specific budget"""
        self.session.execute(
            delete(BudgetParticipantModel).where(BudgetParticipantModel.budget_id == budget_id)
        )

    def delete_by_budget_and_user(self, budget_id: int, user_id: int) -> None:
        """Delete a specific participant relationship"""
        self.session.execute(
            delete(BudgetParticipantModel).where(
                and_(
                    BudgetParticipantModel.budget_id == budget_id,
                    BudgetParticipantModel.user_id == user_id
                )
            )
        )