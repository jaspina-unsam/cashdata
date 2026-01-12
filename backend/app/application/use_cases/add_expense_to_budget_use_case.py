from dataclasses import dataclass
from typing import Optional

from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.entities.budget_expense import BudgetExpense
from app.domain.services.budget_expense_snapshot_service import BudgetExpenseSnapshotService
from app.domain.services.responsibility_calculator import ResponsibilityCalculator
from app.domain.value_objects.split_type import SplitType
from app.domain.value_objects.budget_status import BudgetStatus
from app.application.exceptions.application_exceptions import (
    BusinessRuleViolationError,
    BudgetNotFoundError,
)


@dataclass(frozen=True)
class AddExpenseToBudgetCommand:
    """Command to add an expense to a budget"""
    budget_id: int
    purchase_id: Optional[int]  # XOR with installment_id
    installment_id: Optional[int]  # XOR with purchase_id
    split_type: str  # "equal", "proportional", "custom", "full_single"
    custom_percentages: Optional[dict[int, float]] = None  # {user_id: percentage} for custom split
    responsible_user_id: Optional[int] = None  # Required only for full_single
    requesting_user_id: int = 0  # User making the request


@dataclass(frozen=True)
class AddExpenseToBudgetResult:
    """Result of adding expense to budget"""
    budget_expense_id: int
    success: bool = True


class AddExpenseToBudgetUseCase:
    """Use case for adding an expense (purchase or installment) to a budget"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow
        self._snapshot_service = BudgetExpenseSnapshotService()
        self._responsibility_calculator = ResponsibilityCalculator()

    def execute(self, command: AddExpenseToBudgetCommand) -> AddExpenseToBudgetResult:
        """
        Add an expense to a budget with specified split type.

        Business rules:
        - Budget must exist and be ACTIVE
        - Requesting user must be a participant
        - Purchase XOR installment must exist
        - Expense cannot already be in the budget
        - For proportional split: monthly_incomes must exist for the period
        - For custom split: percentages must sum to 100%
        - For full_single: responsible_user_id must be provided and be a participant
        """
        with self._uow:
            # 1. Validate budget exists and is active
            budget = self._uow.monthly_budgets.find_by_id(command.budget_id)
            if not budget:
                raise BudgetNotFoundError(f"Budget {command.budget_id} not found")

            if budget.status != BudgetStatus.ACTIVE:
                raise BusinessRuleViolationError(
                    f"Cannot add expenses to budget with status '{budget.status.value}'. "
                    "Only ACTIVE budgets can be modified."
                )

            # 2. Validate requesting user is a participant
            participant = self._uow.budget_participants.find_by_budget_and_user(
                command.budget_id, command.requesting_user_id
            )
            if not participant:
                raise BusinessRuleViolationError(
                    f"User {command.requesting_user_id} is not a participant of budget {command.budget_id}"
                )

            # 3. Validate XOR constraint: purchase OR installment, not both or neither
            if (command.purchase_id is None) == (command.installment_id is None):
                raise BusinessRuleViolationError(
                    "Must provide exactly one of purchase_id or installment_id"
                )

            # 4. Get purchase or installment and validate it exists
            purchase = None
            installment = None
            paid_by_user_id = None
            amount = None
            description = None
            date = None

            if command.purchase_id:
                purchase = self._uow.purchases.find_by_id(command.purchase_id)
                if not purchase:
                    raise BusinessRuleViolationError(
                        f"Purchase {command.purchase_id} not found"
                    )
                paid_by_user_id = purchase.user_id
                amount = purchase.amount
                description = purchase.description
                date = purchase.purchase_date

                # Check if this purchase is already in the budget
                existing = self._uow.budget_expenses.find_by_purchase_id(command.purchase_id)
                for exp in existing:
                    if exp.budget_id == command.budget_id:
                        raise BusinessRuleViolationError(
                            f"Purchase {command.purchase_id} is already in budget {command.budget_id}"
                        )

            else:  # installment_id
                installment = self._uow.installments.find_by_id(command.installment_id)
                if not installment:
                    raise BusinessRuleViolationError(
                        f"Installment {command.installment_id} not found"
                    )
                # Get parent purchase for user_id
                parent_purchase = self._uow.purchases.find_by_id(installment.purchase_id)
                if not parent_purchase:
                    raise BusinessRuleViolationError(
                        f"Parent purchase for installment {command.installment_id} not found"
                    )
                paid_by_user_id = parent_purchase.user_id
                amount = installment.amount
                description = parent_purchase.description
                date = parent_purchase.purchase_date

                # Check if this installment is already in the budget
                existing = self._uow.budget_expenses.find_by_installment_id(command.installment_id)
                for exp in existing:
                    if exp.budget_id == command.budget_id:
                        raise BusinessRuleViolationError(
                            f"Installment {command.installment_id} is already in budget {command.budget_id}"
                        )

            # 5. Validate split type
            try:
                split_type = SplitType(command.split_type)
            except ValueError:
                raise BusinessRuleViolationError(
                    f"Invalid split_type: {command.split_type}. "
                    f"Must be one of: {', '.join([st.value for st in SplitType])}"
                )

            # 6. Validate full_single has responsible_user_id
            if split_type == SplitType.FULL_SINGLE and not command.responsible_user_id:
                raise BusinessRuleViolationError(
                    "responsible_user_id is required for split_type 'full_single'"
                )

            # 7. Get all participants for responsibility calculation
            participants = self._uow.budget_participants.find_by_budget_id(command.budget_id)
            participant_user_ids = [p.user_id for p in participants]

            # 8. Validate full_single responsible user is a participant
            if split_type == SplitType.FULL_SINGLE:
                if command.responsible_user_id not in participant_user_ids:
                    raise BusinessRuleViolationError(
                        f"User {command.responsible_user_id} is not a participant of budget {command.budget_id}"
                    )

            # 9. Create snapshot
            snapshot = self._snapshot_service.create_snapshot_from_purchase(
                purchase=purchase,
                installment=installment,
                paid_by_user_id=paid_by_user_id,
                description=description,
                amount=amount,
                date=date,
            )

            # 10. Create BudgetExpense entity
            budget_expense = BudgetExpense(
                id=None,
                budget_id=command.budget_id,
                purchase_id=command.purchase_id,
                installment_id=command.installment_id,
                paid_by_user_id=paid_by_user_id,
                snapshot_description=snapshot["description"],
                snapshot_amount=snapshot["amount"],
                snapshot_currency=snapshot["currency"],
                snapshot_date=snapshot["date"],
                split_type=split_type,
            )

            # 11. Save expense
            saved_expense = self._uow.budget_expenses.save(budget_expense)
            self._uow.flush()

            # 12. Calculate responsibilities
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
                budget_expense_id=saved_expense.id,
                participant_user_ids=participant_user_ids,
                expense_amount=amount,
                split_type=split_type,
                monthly_incomes_map=monthly_incomes_map,
                custom_percentages=command.custom_percentages,
                full_single_user_id=command.responsible_user_id,
            )

            # 13. Save responsibilities
            self._uow.budget_expense_responsibilities.save_many(responsibilities)

            # 14. Commit transaction
            self._uow.commit()

            return AddExpenseToBudgetResult(
                budget_expense_id=saved_expense.id,
                success=True
            )
