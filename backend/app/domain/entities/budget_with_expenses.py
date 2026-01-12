from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict

from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.entities.budget_expense import BudgetExpense
from app.domain.entities.budget_expense_responsibility import BudgetExpenseResponsibility
from app.domain.value_objects.money import Money


@dataclass
class BudgetWithExpenses:
    """
    Aggregate root containing a budget with all its expenses and responsibilities.

    Provides calculation methods for balances and summaries.
    """

    budget: MonthlyBudget
    expenses: List[BudgetExpense]
    responsibilities: Dict[int, List[BudgetExpenseResponsibility]]  # expense_id -> responsibilities

    def total_amount(self) -> Money:
        """Calculate total amount of all expenses in the budget"""
        if not self.expenses:
            return Money(0, "ARS")  # Default currency

        total = sum(expense.amount.amount for expense in self.expenses)
        currency = self.expenses[0].amount.currency
        return Money(total, currency)

    def amount_paid_by(self, user_id: int) -> Money:
        """Calculate total amount paid by a specific user"""
        paid_expenses = [exp for exp in self.expenses if exp.paid_by_user_id == user_id]
        if not paid_expenses:
            return Money(0, "ARS")  # Default currency

        total = sum(expense.amount.amount for expense in paid_expenses)
        currency = paid_expenses[0].amount.currency
        return Money(total, currency)

    def amount_responsible_for(self, user_id: int) -> Money:
        """Calculate total amount a user is responsible for"""
        total = Decimal("0")
        currency = "ARS"  # Default

        for expense in self.expenses:
            expense_responsibilities = self.responsibilities.get(expense.id, [])
            user_responsibility = next(
                (resp for resp in expense_responsibilities if resp.user_id == user_id),
                None
            )
            if user_responsibility:
                total += user_responsibility.responsible_amount.amount
                currency = user_responsibility.responsible_amount.currency

        return Money(total, currency)

    def net_balance(self, user_id: int) -> Money:
        """Calculate net balance for a user (paid - responsible)"""
        paid = self.amount_paid_by(user_id)
        responsible = self.amount_responsible_for(user_id)
        return paid - responsible

    def get_participants(self) -> List[int]:
        """Get list of all participant user IDs"""
        participant_ids = set()

        # Add creator
        participant_ids.add(self.budget.created_by_user_id)

        # Add users from responsibilities
        for expense_responsibilities in self.responsibilities.values():
            for resp in expense_responsibilities:
                participant_ids.add(resp.user_id)

        return sorted(list(participant_ids))

    def calculate_debt_summary(self) -> List[Dict]:
        """
        Calculate summary of debts between participants.

        Returns list of dicts with format:
        [
            {"from_user_id": 1, "to_user_id": 2, "amount": Money(5000, "ARS")},
            ...
        ]
        """
        participants = self.get_participants()
        balances = {user_id: self.net_balance(user_id) for user_id in participants}

        # Simple debt calculation: positive balance users owe to negative balance users
        debts = []

        # Get users with positive balances (creditors) and negative balances (debtors)
        creditors = [(uid, bal) for uid, bal in balances.items() if bal.amount > 0]
        debtors = [(uid, bal) for uid, bal in balances.items() if bal.amount < 0]

        # Sort by amount (largest first)
        creditors.sort(key=lambda x: x[1].amount, reverse=True)
        debtors.sort(key=lambda x: x[1].amount)  # Most negative first

        for debtor_id, debtor_balance in debtors:
            debtor_amount = abs(debtor_balance.amount)

            for creditor_id, creditor_balance in creditors:
                if debtor_amount <= 0:
                    break

                creditor_amount = creditor_balance.amount
                if creditor_amount <= 0:
                    continue

                debt_amount = min(debtor_amount, creditor_amount)

                if debt_amount > 0:
                    debts.append({
                        "from_user_id": debtor_id,
                        "to_user_id": creditor_id,
                        "amount": Money(debt_amount, debtor_balance.currency)
                    })

                debtor_amount -= debt_amount

        return debts