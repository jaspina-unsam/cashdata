from dataclasses import dataclass
from typing import Optional

from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.services.responsibility_calculator import ResponsibilityCalculator
from app.domain.value_objects.split_type import SplitType
from app.domain.value_objects.budget_status import BudgetStatus
from app.application.exceptions.application_exceptions import (
    BusinessRuleViolationError,
    BudgetExpenseNotFoundError,
)


@dataclass(frozen=True)
class UpdateExpenseResponsibilitiesCommand:
    """Command to update expense responsibilities (change split type/percentages)"""
    budget_expense_id: int
    split_type: str  # "equal", "proportional", "custom", "full_single"
    custom_percentages: Optional[dict[int, float]] = None  # {user_id: percentage}
    responsible_user_id: Optional[int] = None  # Required only for full_single
    requesting_user_id: int = 0  # User making the request


@dataclass(frozen=True)
class UpdateExpenseResponsibilitiesResult:
    """Result of updating expense responsibilities"""
    success: bool = True


class UpdateExpenseResponsibilitiesUseCase:
    """Use case for updating split type and responsibilities for a budget expense"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow
        self._responsibility_calculator = ResponsibilityCalculator()

    def execute(self, command: UpdateExpenseResponsibilitiesCommand) -> UpdateExpenseResponsibilitiesResult:
        """
        Update the split type and responsibilities for an expense.

        Business rules:
        - Budget expense must exist
        - Budget must be ACTIVE (cannot edit closed/archived budgets)
        - Requesting user must be a participant of the budget
        - For proportional split: monthly_incomes must exist
        - For custom split: percentages must sum to 100%
        - For full_single: responsible_user_id must be provided and be a participant
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

            # 4. Validate split type
            try:
                split_type = SplitType(command.split_type)
            except ValueError:
                raise BusinessRuleViolationError(
                    f"Invalid split_type: {command.split_type}. "
                    f"Must be one of: {', '.join([st.value for st in SplitType])}"
                )

            # 5. Validate full_single has responsible_user_id
            if split_type == SplitType.FULL_SINGLE and not command.responsible_user_id:
                raise BusinessRuleViolationError(
                    "responsible_user_id is required for split_type 'full_single'"
                )

            # 6. Get all participants
            participants = self._uow.budget_participants.find_by_budget_id(budget.id)
            participant_user_ids = [p.user_id for p in participants]

            # 7. Validate full_single responsible user is a participant
            if split_type == SplitType.FULL_SINGLE:
                if command.responsible_user_id not in participant_user_ids:
                    raise BusinessRuleViolationError(
                        f"User {command.responsible_user_id} is not a participant of budget {budget.id}"
                    )

            # 8. Delete current responsibilities
            self._uow.budget_expense_responsibilities.delete_by_budget_expense_id(
                command.budget_expense_id
            )

            # 9. Update expense split_type
            updated_expense = BudgetExpense(
                id=expense.id,
                budget_id=expense.budget_id,
                purchase_id=expense.purchase_id,
                installment_id=expense.installment_id,
                paid_by_user_id=expense.paid_by_user_id,
                snapshot_description=expense.snapshot_description,
                snapshot_amount=expense.snapshot_amount,
                snapshot_currency=expense.snapshot_currency,
                snapshot_date=expense.snapshot_date,
                split_type=split_type,
            )
            self._uow.budget_expenses.save(updated_expense)

            # 10. Calculate new responsibilities
            # For proportional, get monthly_incomes
            monthly_incomes_map = {}
            if split_type == SplitType.PROPORTIONAL:
                monthly_incomes = self._uow.monthly_incomes.find_by_period_and_users(
                    budget.period, participant_user_ids
                )
                monthly_incomes_map = {mi.user_id: mi for mi in monthly_incomes}

                # Validate all participants have income defined
                for user_id in participant_user_ids:
                    if user_id not in monthly_incomes_map:
                        raise BusinessRuleViolationError(
                            f"User {user_id} has no monthly_income defined for period {budget.period.to_string()}. "
                            "All participants must have income defined to use proportional split."
                        )

            responsibilities = self._responsibility_calculator.calculate_responsibilities(
                budget_expense_id=expense.id,
                participant_user_ids=participant_user_ids,
                expense_amount=expense.snapshot_amount,
                split_type=split_type,
                monthly_incomes_map=monthly_incomes_map,
                custom_percentages=command.custom_percentages,
                full_single_user_id=command.responsible_user_id,
            )

            # 11. Save new responsibilities
            self._uow.budget_expense_responsibilities.save_many(responsibilities)

            # 12. Commit transaction
            self._uow.commit()

            return UpdateExpenseResponsibilitiesResult(success=True)


# Import BudgetExpense to avoid circular import issues
from app.domain.entities.budget_expense import BudgetExpense
