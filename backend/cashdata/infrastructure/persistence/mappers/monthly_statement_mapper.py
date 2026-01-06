"""Mapper for monthly statement entity and model."""

from cashdata.domain.entities.monthly_statement import MonthlyStatement
from cashdata.infrastructure.persistence.models.monthly_statement_model import (
    MonthlyStatementModel,
)


class MonthlyStatementMapper:
    """Maps between MonthlyStatement entity and MonthlyStatementModel."""

    @staticmethod
    def to_entity(model: MonthlyStatementModel) -> MonthlyStatement:
        """Convert a model to an entity.

        Args:
            model: The MonthlyStatementModel to convert

        Returns:
            The corresponding MonthlyStatement entity
        """
        return MonthlyStatement(
            id=model.id,
            credit_card_id=model.credit_card_id,
            start_date=model.start_date,
            closing_date=model.closing_date,
            due_date=model.due_date,
        )

    @staticmethod
    def to_model(entity: MonthlyStatement) -> MonthlyStatementModel:
        """Convert an entity to a model.

        Args:
            entity: The MonthlyStatement entity to convert

        Returns:
            The corresponding MonthlyStatementModel
        """
        return MonthlyStatementModel(
            id=entity.id,
            credit_card_id=entity.credit_card_id,
            start_date=entity.start_date,
            closing_date=entity.closing_date,
            due_date=entity.due_date,
        )
