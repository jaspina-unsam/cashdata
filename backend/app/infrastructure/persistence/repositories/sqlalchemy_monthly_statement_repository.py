"""SQLAlchemy implementation of monthly statement repository."""

from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.domain.entities.monthly_statement import MonthlyStatement
from app.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)
from app.infrastructure.persistence.mappers.monthly_statement_mapper import (
    MonthlyStatementMapper,
)
from app.infrastructure.persistence.models.credit_card_model import CreditCardModel
from app.infrastructure.persistence.models.monthly_statement_model import (
    MonthlyStatementModel,
)


class SQLAlchemyMonthlyStatementRepository(IMonthlyStatementRepository):
    """SQLAlchemy implementation of monthly statement repository."""

    def __init__(self, session: Session):
        """Initialize the repository.

        Args:
            session: The SQLAlchemy session
        """
        self._session = session

    def find_by_id(self, statement_id: int) -> MonthlyStatement | None:
        """Find a monthly statement by its ID."""
        stmt = select(MonthlyStatementModel).where(
            MonthlyStatementModel.id == statement_id
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return MonthlyStatementMapper.to_entity(model) if model else None

    def find_by_credit_card_id(
        self, credit_card_id: int, include_future: bool = False
    ) -> list[MonthlyStatement]:
        """Find all statements for a credit card."""
        query = select(MonthlyStatementModel).where(
            MonthlyStatementModel.credit_card_id == credit_card_id
        )

        if not include_future:
            today = date.today()
            query = query.where(MonthlyStatementModel.due_date <= today)

        # Order by due_date descending (most recent first)
        query = query.order_by(MonthlyStatementModel.due_date.desc())

        models = self._session.execute(query).scalars().all()
        return [MonthlyStatementMapper.to_entity(model) for model in models]

    def find_all_by_user_id(
        self, user_id: int, include_future: bool = False
    ) -> list[MonthlyStatement]:
        """Find all statements for all credit cards owned by a user."""
        query = (
            select(MonthlyStatementModel)
            .join(
                CreditCardModel,
                MonthlyStatementModel.credit_card_id == CreditCardModel.id,
            )
            .where(CreditCardModel.user_id == user_id)
        )

        if not include_future:
            today = date.today()
            query = query.where(MonthlyStatementModel.due_date <= today)

        # Order by due_date descending (most recent first)
        query = query.order_by(MonthlyStatementModel.due_date.desc())

        models = self._session.execute(query).scalars().all()
        return [MonthlyStatementMapper.to_entity(model) for model in models]

    def save(self, statement: MonthlyStatement) -> MonthlyStatement:
        """Save a monthly statement (create or update)."""
        if statement.id is None:
            # Create new statement
            model = MonthlyStatementMapper.to_model(statement)
            self._session.add(model)
            self._session.flush()
            return MonthlyStatementMapper.to_entity(model)
        else:
            # Update existing statement
            stmt = select(MonthlyStatementModel).where(
                MonthlyStatementModel.id == statement.id
            )
            model = self._session.execute(stmt).scalar_one()
            model.credit_card_id = statement.credit_card_id
            model.start_date = statement.start_date
            model.closing_date = statement.closing_date
            model.due_date = statement.due_date
            self._session.flush()
            return MonthlyStatementMapper.to_entity(model)

    def get_previous_statement(
        self, credit_card_id: int, closing_date: date
    ) -> MonthlyStatement | None:
        """Get the previous statement for a credit card."""
        stmt = (
            select(MonthlyStatementModel)
            .where(
                and_(
                    MonthlyStatementModel.credit_card_id == credit_card_id,
                    MonthlyStatementModel.closing_date < closing_date,
                )
            )
            .order_by(MonthlyStatementModel.closing_date.desc())
            .limit(1)
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return MonthlyStatementMapper.to_entity(model) if model else None
