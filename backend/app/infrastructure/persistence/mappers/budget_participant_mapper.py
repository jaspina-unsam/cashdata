from app.domain.entities.budget_participant import BudgetParticipant
from app.infrastructure.persistence.models.budget_participant_model import BudgetParticipantModel


class BudgetParticipantMapper:
    @staticmethod
    def to_entity(model: BudgetParticipantModel) -> BudgetParticipant:
        """SQLAlchemy Model → Domain Entity"""
        return BudgetParticipant(
            id=model.id,
            budget_id=model.budget_id,
            user_id=model.user_id,
        )

    @staticmethod
    def to_model(entity: BudgetParticipant) -> BudgetParticipantModel:
        """Domain Entity → SQLAlchemy Model"""
        return BudgetParticipantModel(
            id=entity.id,
            budget_id=entity.budget_id,
            user_id=entity.user_id,
        )