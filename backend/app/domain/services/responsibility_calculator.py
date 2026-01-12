from typing import List, Dict, Optional
from decimal import Decimal, ROUND_HALF_UP

from app.domain.entities.user import User
from app.domain.entities.monthly_income import MonthlyIncome
from app.domain.entities.budget_expense_responsibility import BudgetExpenseResponsibility
from app.domain.services.apportionment_calculator import ApportionmentCalculator
from app.domain.value_objects.money import Money
from app.domain.value_objects.period import Period
from app.domain.value_objects.percentage import Percentage
from app.domain.value_objects.split_type import SplitType
from app.domain.exceptions.domain_exceptions import InvalidCalculation


class ResponsibilityCalculator:
    """
    Domain Service to calculate expense responsibilities based on split type.

    Supports different split types: equal, proportional, custom, full_single.
    """

    def __init__(self, apportionment_calculator: Optional[ApportionmentCalculator] = None):
        self._apportionment_calculator = apportionment_calculator or ApportionmentCalculator()

    def calculate_responsibilities(
        self,
        expense_id: int,
        budget_id: int,
        amount: Money,
        split_type: SplitType,
        participants: List[User],
        period: Period,
        incomes: Optional[List[MonthlyIncome]] = None,
        custom_percentages: Optional[Dict[int, Decimal]] = None,
        full_single_user_id: Optional[int] = None
    ) -> List[BudgetExpenseResponsibility]:
        """
        Calculate responsibilities for an expense based on split type.

        Args:
            expense_id: ID of the budget expense
            budget_id: ID of the budget (for context)
            amount: Total amount to split
            split_type: How to split the expense
            participants: List of users participating in the budget
            period: Budget period (for proportional calculations)
            incomes: Monthly incomes for proportional split
            custom_percentages: Custom percentages for CUSTOM split (user_id -> percentage)
            full_single_user_id: User ID for FULL_SINGLE split

        Returns:
            List of BudgetExpenseResponsibility entities

        Raises:
            InvalidCalculation: If split configuration is invalid
        """
        if not participants:
            raise InvalidCalculation("At least one participant is required")

        if split_type == SplitType.EQUAL:
            return self._calculate_equal_split(expense_id, amount, participants)
        elif split_type == SplitType.PROPORTIONAL:
            return self._calculate_proportional_split(
                expense_id, amount, participants, period, incomes or []
            )
        elif split_type == SplitType.CUSTOM:
            return self._calculate_custom_split(
                expense_id, amount, participants, custom_percentages or {}
            )
        elif split_type == SplitType.FULL_SINGLE:
            return self._calculate_full_single_split(
                expense_id, amount, participants, full_single_user_id
            )
        else:
            raise InvalidCalculation(f"Unsupported split type: {split_type}")

    def _calculate_equal_split(
        self,
        expense_id: int,
        amount: Money,
        participants: List[User]
    ) -> List[BudgetExpenseResponsibility]:
        """Calculate equal split among all participants"""
        num_participants = len(participants)
        equal_amount = amount.amount / Decimal(str(num_participants))

        responsibilities = []
        total_assigned = Decimal("0")

        for i, user in enumerate(participants):
            if i == num_participants - 1:
                # Last participant gets the remaining amount to ensure total sums correctly
                responsible_amount_value = amount.amount - total_assigned
            else:
                responsible_amount_value = equal_amount.quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                total_assigned += responsible_amount_value

            responsible_amount = Money(responsible_amount_value, amount.currency)
            percentage = (responsible_amount_value / amount.amount) * Decimal("100")

            responsibilities.append(BudgetExpenseResponsibility(
                id=None,
                budget_expense_id=expense_id,
                user_id=user.id,
                percentage=percentage.quantize(Decimal("0.01")),
                responsible_amount=responsible_amount
            ))

        # Adjust the last percentage to ensure sum is exactly 100%
        if responsibilities:
            total_percentage_so_far = sum(r.percentage for r in responsibilities[:-1])
            responsibilities[-1] = BudgetExpenseResponsibility(
                id=None,
                budget_expense_id=expense_id,
                user_id=responsibilities[-1].user_id,
                percentage=Decimal("100") - total_percentage_so_far,
                responsible_amount=responsibilities[-1].responsible_amount
            )

        return responsibilities

    def _calculate_proportional_split(
        self,
        expense_id: int,
        amount: Money,
        participants: List[User],
        period: Period,
        incomes: List[MonthlyIncome]
    ) -> List[BudgetExpenseResponsibility]:
        """Calculate proportional split based on monthly incomes"""
        percentages = self._apportionment_calculator.calculate_percentages(
            participants, incomes, period
        )

        responsibilities = []
        for user in participants:
            percentage = percentages[user.id].value
            responsible_amount = self._calculate_amount_from_percentage(amount, percentage)

            responsibilities.append(BudgetExpenseResponsibility(
                id=None,
                budget_expense_id=expense_id,
                user_id=user.id,
                percentage=percentage,
                responsible_amount=responsible_amount
            ))

        return responsibilities

    def _calculate_custom_split(
        self,
        expense_id: int,
        amount: Money,
        participants: List[User],
        custom_percentages: Dict[int, Decimal]
    ) -> List[BudgetExpenseResponsibility]:
        """Calculate custom split with provided percentages"""
        # Validate that all participants have percentages
        participant_ids = {user.id for user in participants}
        provided_ids = set(custom_percentages.keys())

        if participant_ids != provided_ids:
            missing = participant_ids - provided_ids
            extra = provided_ids - participant_ids
            raise InvalidCalculation(
                f"Custom percentages must be provided for all participants. "
                f"Missing: {missing}, Extra: {extra}"
            )

        # Validate percentages sum to 100
        total_percentage = sum(custom_percentages.values())
        if total_percentage != Decimal("100"):
            raise InvalidCalculation(
                f"Custom percentages must sum to 100%, got {total_percentage}%"
            )

        responsibilities = []
        for user in participants:
            percentage = custom_percentages[user.id]
            responsible_amount = self._calculate_amount_from_percentage(amount, percentage)

            responsibilities.append(BudgetExpenseResponsibility(
                id=None,
                budget_expense_id=expense_id,
                user_id=user.id,
                percentage=percentage,
                responsible_amount=responsible_amount
            ))

        return responsibilities

    def _calculate_full_single_split(
        self,
        expense_id: int,
        amount: Money,
        participants: List[User],
        full_single_user_id: Optional[int]
    ) -> List[BudgetExpenseResponsibility]:
        """Calculate full responsibility for one user"""
        if full_single_user_id is None:
            raise InvalidCalculation("full_single_user_id is required for FULL_SINGLE split")

        # Validate user is a participant
        participant_ids = {user.id for user in participants}
        if full_single_user_id not in participant_ids:
            raise InvalidCalculation(
                f"User {full_single_user_id} is not a participant in this budget"
            )

        responsibilities = []
        for user in participants:
            if user.id == full_single_user_id:
                percentage = Decimal("100")
                responsible_amount = amount
            else:
                percentage = Decimal("0")
                responsible_amount = Money(0, amount.currency)

            responsibilities.append(BudgetExpenseResponsibility(
                id=None,
                budget_expense_id=expense_id,
                user_id=user.id,
                percentage=percentage,
                responsible_amount=responsible_amount
            ))

        return responsibilities

    def _calculate_amount_from_percentage(self, total_amount: Money, percentage: Decimal) -> Money:
        """Calculate amount for a given percentage of total"""
        amount = (total_amount.amount * percentage / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return Money(amount, total_amount.currency)