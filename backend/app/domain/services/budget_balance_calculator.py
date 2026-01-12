from typing import Dict, List

from app.domain.entities.budget_with_expenses import BudgetWithExpenses
from app.domain.value_objects.money import Money


class BudgetBalanceCalculator:
    """
    Domain Service to calculate balances and debt summaries for budgets.
    """

    def calculate_balance(
        self,
        budget: BudgetWithExpenses,
        user_id: int
    ) -> Money:
        """
        Calculate the net balance for a user in the budget.

        Positive balance means the user is owed money (paid more than responsible).
        Negative balance means the user owes money (responsible for more than paid).

        Args:
            budget: The budget with expenses and responsibilities
            user_id: The user to calculate balance for

        Returns:
            Net balance as Money (positive = owed, negative = owes)
        """
        paid = budget.amount_paid_by(user_id)
        responsible = budget.amount_responsible_for(user_id)
        return paid - responsible

    def calculate_debt_summary(
        self,
        budget: BudgetWithExpenses
    ) -> List[Dict]:
        """
        Calculate a summary of debts between participants.

        This delegates to the aggregate method for consistency.

        Args:
            budget: The budget with expenses and responsibilities

        Returns:
            List of debt dictionaries with format:
            [
                {"from_user_id": int, "to_user_id": int, "amount": Money},
                ...
            ]
        """
        return budget.calculate_debt_summary()