from app.domain.entities.budget_expense import BudgetExpense
from app.domain.value_objects.money import Money
from app.domain.value_objects.split_type import SplitType
from app.infrastructure.persistence.models.budget_expense_model import BudgetExpenseModel


class BudgetExpenseMapper:
    @staticmethod
    def to_entity(model: BudgetExpenseModel) -> BudgetExpense:
        """SQLAlchemy Model → Domain Entity"""
        return BudgetExpense(
            id=model.id,
            budget_id=model.budget_id,
            purchase_id=model.purchase_id,
            installment_id=model.installment_id,
            paid_by_user_id=model.paid_by_user_id,
            split_type=SplitType(model.split_type),
            amount=Money(model.amount, model.currency),
            currency=model.currency,
            description=model.description,
            date=model.date,
            payment_method_name=model.payment_method_name,
            created_at=model.created_at.date(),  # Convert datetime to date
        )

    @staticmethod
    def to_model(entity: BudgetExpense) -> BudgetExpenseModel:
        """Domain Entity → SQLAlchemy Model"""
        return BudgetExpenseModel(
            id=entity.id,
            budget_id=entity.budget_id,
            purchase_id=entity.purchase_id,
            installment_id=entity.installment_id,
            paid_by_user_id=entity.paid_by_user_id,
            split_type=entity.split_type.value,
            amount=entity.amount.amount,
            currency=entity.currency,
            description=entity.description,
            date=entity.date,
            payment_method_name=entity.payment_method_name,
            created_at=entity.created_at,  # This will be converted to datetime in the model
        )