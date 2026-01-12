from app.domain.entities.budget_expense_responsibility import BudgetExpenseResponsibility
from app.domain.value_objects.money import Money
from app.infrastructure.persistence.models.budget_expense_responsibility_model import BudgetExpenseResponsibilityModel


class BudgetExpenseResponsibilityMapper:
    @staticmethod
    def to_entity(model: BudgetExpenseResponsibilityModel) -> BudgetExpenseResponsibility:
        """SQLAlchemy Model → Domain Entity"""
        return BudgetExpenseResponsibility(
            id=model.id,
            budget_expense_id=model.budget_expense_id,
            user_id=model.user_id,
            percentage=model.percentage,
            responsible_amount=Money(model.responsible_amount, model.responsible_currency),
        )

    @staticmethod
    def to_model(entity: BudgetExpenseResponsibility) -> BudgetExpenseResponsibilityModel:
        """Domain Entity → SQLAlchemy Model"""
        return BudgetExpenseResponsibilityModel(
            id=entity.id,
            budget_expense_id=entity.budget_expense_id,
            user_id=entity.user_id,
            percentage=entity.percentage,
            responsible_amount=entity.responsible_amount.amount,
            responsible_currency=entity.responsible_amount.currency,
        )