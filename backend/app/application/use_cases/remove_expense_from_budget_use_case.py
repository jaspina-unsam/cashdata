from dataclasses import dataclass

from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.value_objects.budget_status import BudgetStatus
from app.application.exceptions.application_exceptions import (
    BusinessRuleViolationError,
    BudgetExpenseNotFoundError,
)


@dataclass(frozen=True)
class RemoveExpenseFromBudgetCommand:
    """Command to remove an expense from a budget"""
    budget_expense_id: int
    requesting_user_id: int  # User making the request


@dataclass(frozen=True)
class RemoveExpenseFromBudgetResult:
    """Result of removing expense from budget"""
    success: bool = True


class RemoveExpenseFromBudgetUseCase:
    """Use case for removing an expense from a budget"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, command: RemoveExpenseFromBudgetCommand) -> RemoveExpenseFromBudgetResult:
        """
        Remove an expense from a budget (hard delete).

        Business rules:
        - Budget expense must exist
        - Budget must be ACTIVE (cannot modify closed/archived budgets)
        - Requesting user must be a participant of the budget
        - Deleting the expense will cascade delete all responsibilities
        """
        with self._uow:
            # 1. Get budget expense
            expense = self._uow.budget_expenses.find_by_id(command.budget_expense_id)
            if not expense:
                raise BudgetExpenseNotFoundError(
                    f"Budget expense {command.budget_expense_id} not found"
                )

            # 2. Get budget and validate it's active
            budget = self._uow.monthly_budgets.find_by_id(expense.budget_id)
            if not budget:
                raise BusinessRuleViolationError(
                    f"Budget {expense.budget_id} not found"
                )

            if budget.status != BudgetStatus.ACTIVE:
                raise BusinessRuleViolationError(
                    f"Cannot modify expenses in budget with status '{budget.status.value}'. "
                    "Only ACTIVE budgets can be modified."
                )

            # 3. Validate requesting user is a participant
            participant = self._uow.budget_participants.find_by_budget_and_user(
                budget.id, command.requesting_user_id
            )
            if not participant:
                raise BusinessRuleViolationError(
                    f"User {command.requesting_user_id} is not a participant of budget {budget.id}"
                )

            # 4. Delete responsibilities (explicit, though DB cascade should handle it)
            self._uow.budget_expense_responsibilities.delete_by_budget_expense_id(
                command.budget_expense_id
            )

            # 5. Delete expense
            self._uow.budget_expenses.delete(command.budget_expense_id)

            # 6. Commit transaction
            self._uow.commit()

            return RemoveExpenseFromBudgetResult(success=True)
