from typing import List, Dict
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.entities.budget_expense import BudgetExpense
from app.domain.entities.budget_expense_responsibility import BudgetExpenseResponsibility
from app.domain.entities.budget_with_expenses import BudgetWithExpenses
from app.domain.entities.user import User
from app.application.dtos.monthly_budget_dto import (
    MonthlyBudgetResponseDTO,
    BudgetDetailsDTO,
    BudgetExpenseDTO,
    BudgetExpenseResponsibilityDTO,
    BudgetBalanceDTO,
    BudgetDebtDTO,
)
from app.application.mappers.monthly_budget_dto_mapper import MonthlyBudgetDTOMapper
from app.application.exceptions.application_exceptions import BusinessRuleViolationError


class GetBudgetDetailsUseCase:
    """Use case for getting complete budget details with expenses and balances"""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, budget_id: int, requesting_user_id: int) -> BudgetDetailsDTO:
        """
        Get complete budget details including expenses, responsibilities, and balances

        Args:
            budget_id: ID of the budget to retrieve
            requesting_user_id: ID of the user making the request (for authorization)

        Returns:
            BudgetDetailsDTO: Complete budget data with expenses and balances

        Raises:
            BusinessRuleViolationError: If budget not found or user not authorized
        """
        with self._uow:
            # 1. Find budget
            budget = self._uow.monthly_budgets.find_by_id(budget_id)
            if not budget:
                raise BusinessRuleViolationError(f"Budget with ID {budget_id} not found")

            # 2. Check if requesting user is a participant
            is_participant = self._uow.budget_participants.find_by_budget_and_user(budget_id, requesting_user_id)
            if not is_participant:
                raise BusinessRuleViolationError(f"User {requesting_user_id} is not authorized to view budget {budget_id}")

            # 3. Get all participants
            participants = self._uow.budget_participants.find_by_budget_id(budget_id)
            participant_count = len(participants)
            participant_ids = [p.user_id for p in participants]
            
            # 4. Get all expenses for this budget
            expenses = self._uow.budget_expenses.find_by_budget_id(budget_id)
            
            # 5. Get all responsibilities for each expense
            responsibilities_dict: Dict[int, List[BudgetExpenseResponsibility]] = {}
            for expense in expenses:
                responsibilities = self._uow.budget_expense_responsibilities.find_by_budget_expense_id(expense.id)
                responsibilities_dict[expense.id] = responsibilities
            
            # 6. Get user information for names
            users_dict: Dict[int, User] = {}
            for user_id in participant_ids:
                user = self._uow.users.find_by_id(user_id)
                if user:
                    users_dict[user_id] = user
            
            # 7. Create BudgetWithExpenses aggregate for calculations
            budget_aggregate = BudgetWithExpenses(
                budget=budget,
                expenses=expenses,
                responsibilities=responsibilities_dict
            )
            
            # 8. Calculate balances for each participant
            balances = []
            for user_id in participant_ids:
                user = users_dict.get(user_id)
                user_name = user.name if user else f"User {user_id}"
                
                paid = budget_aggregate.amount_paid_by(user_id)
                responsible = budget_aggregate.amount_responsible_for(user_id)
                balance = paid - responsible
                
                balances.append(BudgetBalanceDTO(
                    user_id=user_id,
                    user_name=user_name,
                    paid=paid.amount,
                    responsible=responsible.amount,
                    balance=balance.amount,
                    currency=paid.currency
                ))
            
            # 9. Calculate debt summary
            debt_summary_raw = budget_aggregate.calculate_debt_summary()
            debt_summary = []
            for debt in debt_summary_raw:
                from_user = users_dict.get(debt["from_user_id"])
                to_user = users_dict.get(debt["to_user_id"])
                debt_summary.append(BudgetDebtDTO(
                    from_user_id=debt["from_user_id"],
                    from_user_name=from_user.name if from_user else f"User {debt['from_user_id']}",
                    to_user_id=debt["to_user_id"],
                    to_user_name=to_user.name if to_user else f"User {debt['to_user_id']}",
                    amount=debt["amount"].amount,
                    currency=debt["amount"].currency
                ))
            
            # 10. Convert expenses to DTOs with user names
            expense_dtos = []
            for expense in expenses:
                paid_by_user = users_dict.get(expense.paid_by_user_id)
                expense_dtos.append(BudgetExpenseDTO(
                    id=expense.id,
                    budget_id=expense.budget_id,
                    purchase_id=expense.purchase_id,
                    installment_id=expense.installment_id,
                    paid_by_user_id=expense.paid_by_user_id,
                    paid_by_user_name=paid_by_user.name if paid_by_user else None,
                    snapshot_description=expense.description,
                    snapshot_amount=expense.amount.amount,
                    snapshot_currency=expense.amount.currency,
                    snapshot_date=expense.date.isoformat(),
                    split_type=expense.split_type
                ))
            
            # 11. Convert responsibilities to DTOs with user names
            responsibilities_dtos: Dict[int, List[BudgetExpenseResponsibilityDTO]] = {}
            for expense_id, resps in responsibilities_dict.items():
                responsibilities_dtos[expense_id] = [
                    BudgetExpenseResponsibilityDTO(
                        id=resp.id,
                        budget_expense_id=resp.budget_expense_id,
                        user_id=resp.user_id,
                        user_name=users_dict.get(resp.user_id).name if users_dict.get(resp.user_id) else None,
                        percentage=resp.percentage,
                        responsible_amount=resp.responsible_amount.amount,
                        currency=resp.responsible_amount.currency
                    )
                    for resp in resps
                ]
            
            # 12. Build budget response DTO
            budget_dto = MonthlyBudgetDTOMapper.to_response_dto(budget, participant_count)
            
        # 13. Return complete details
        return BudgetDetailsDTO(
            budget=budget_dto,
            expenses=expense_dtos,
            responsibilities=responsibilities_dtos,
            balances=balances,
            debt_summary=debt_summary
        )