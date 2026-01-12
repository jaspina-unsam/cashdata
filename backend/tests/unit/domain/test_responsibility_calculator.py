# backend/tests/unit/domain/test_responsibility_calculator.py
import pytest
from decimal import Decimal
from unittest.mock import Mock
from app.domain.services.responsibility_calculator import ResponsibilityCalculator
from app.domain.entities.user import User
from app.domain.entities.monthly_income import MonthlyIncome
from app.domain.value_objects.money import Money
from app.domain.value_objects.period import Period
from app.domain.value_objects.percentage import Percentage
from app.domain.value_objects.split_type import SplitType
from app.domain.exceptions.domain_exceptions import InvalidCalculation


class TestResponsibilityCalculatorEqualSplit:
    """Tests para split EQUAL"""

    def test_calculate_equal_split_two_participants(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2)]
        amount = Money(10000, "ARS")

        responsibilities = calculator.calculate_responsibilities(
            expense_id=1,
            budget_id=1,
            amount=amount,
            split_type=SplitType.EQUAL,
            participants=users,
            period=Period(2026, 1)
        )

        assert len(responsibilities) == 2

        # Check percentages
        resp1 = next(r for r in responsibilities if r.user_id == 1)
        resp2 = next(r for r in responsibilities if r.user_id == 2)

        assert resp1.percentage == Decimal("50")
        assert resp2.percentage == Decimal("50")

        # Check amounts
        assert resp1.responsible_amount == Money(5000, "ARS")
        assert resp2.responsible_amount == Money(5000, "ARS")

    def test_calculate_equal_split_three_participants(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2), self._create_user(3)]
        amount = Money(10000, "ARS")

        responsibilities = calculator.calculate_responsibilities(
            expense_id=1,
            budget_id=1,
            amount=amount,
            split_type=SplitType.EQUAL,
            participants=users,
            period=Period(2026, 1)
        )

        assert len(responsibilities) == 3

        # Check percentages sum to 100
        total_percentage = sum(r.percentage for r in responsibilities)
        assert total_percentage == Decimal("100")

        # Check amounts sum to total
        total_amount = sum(r.responsible_amount.amount for r in responsibilities)
        assert total_amount == Decimal("10000")

    def test_calculate_equal_split_rounding(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2), self._create_user(3)]
        amount = Money(100, "ARS")  # Amount not divisible by 3

        responsibilities = calculator.calculate_responsibilities(
            expense_id=1,
            budget_id=1,
            amount=amount,
            split_type=SplitType.EQUAL,
            participants=users,
            period=Period(2026, 1)
        )

        # Check percentages sum to 100
        total_percentage = sum(r.percentage for r in responsibilities)
        assert total_percentage == Decimal("100")

        # Check amounts sum to total
        total_amount = sum(r.responsible_amount.amount for r in responsibilities)
        assert total_amount == Decimal("100")

    def _create_user(self, user_id: int) -> User:
        """Helper to create test user"""
        return User(
            id=user_id,
            name=f"User {user_id}",
            email=f"user{user_id}@example.com",
            wage=Money(50000, "ARS"),
            is_deleted=False,
            deleted_at=None
        )


class TestResponsibilityCalculatorProportionalSplit:
    """Tests para split PROPORTIONAL"""

    def test_calculate_proportional_split_with_incomes(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2)]
        period = Period(2026, 1)
        incomes = [
            MonthlyIncome(id=1, user_id=1, period=period, amount=Money(60000, "ARS")),
            MonthlyIncome(id=2, user_id=2, period=period, amount=Money(40000, "ARS"))
        ]
        amount = Money(10000, "ARS")

        responsibilities = calculator.calculate_responsibilities(
            expense_id=1,
            budget_id=1,
            amount=amount,
            split_type=SplitType.PROPORTIONAL,
            participants=users,
            period=period,
            incomes=incomes
        )

        assert len(responsibilities) == 2

        resp1 = next(r for r in responsibilities if r.user_id == 1)
        resp2 = next(r for r in responsibilities if r.user_id == 2)

        # User 1: 60% (60000/100000), User 2: 40% (40000/100000)
        assert resp1.percentage == Decimal("60")
        assert resp2.percentage == Decimal("40")

        assert resp1.responsible_amount == Money(6000, "ARS")
        assert resp2.responsible_amount == Money(4000, "ARS")

    def test_calculate_proportional_split_without_incomes_falls_back_to_equal(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2)]
        period = Period(2026, 1)
        incomes = [
            MonthlyIncome(id=1, user_id=1, period=period, amount=Money(60000, "ARS"), created_at=None),
            MonthlyIncome(id=2, user_id=2, period=period, amount=Money(40000, "ARS"), created_at=None)
        ]
        amount = Money(10000, "ARS")

        responsibilities = calculator.calculate_responsibilities(
            expense_id=1,
            budget_id=1,
            amount=amount,
            split_type=SplitType.PROPORTIONAL,
            participants=users,
            period=period,
            incomes=incomes
        )

        assert len(responsibilities) == 2

        resp1 = next(r for r in responsibilities if r.user_id == 1)
        resp2 = next(r for r in responsibilities if r.user_id == 2)

        # User 1: 60% (60000/100000), User 2: 40% (40000/100000)
        assert resp1.percentage == Decimal("60")
        assert resp2.percentage == Decimal("40")

        assert resp1.responsible_amount == Money(6000, "ARS")
        assert resp2.responsible_amount == Money(4000, "ARS")

    def test_calculate_proportional_split_without_incomes_falls_back_to_equal(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2)]
        period = Period(2026, 1)
        amount = Money(10000, "ARS")

        responsibilities = calculator.calculate_responsibilities(
            expense_id=1,
            budget_id=1,
            amount=amount,
            split_type=SplitType.PROPORTIONAL,
            participants=users,
            period=period,
            incomes=[]  # No incomes
        )

        assert len(responsibilities) == 2

        resp1 = next(r for r in responsibilities if r.user_id == 1)
        resp2 = next(r for r in responsibilities if r.user_id == 2)

        # Falls back to equal split
        assert resp1.percentage == Decimal("50")
        assert resp2.percentage == Decimal("50")

    def _create_user(self, user_id: int) -> User:
        """Helper to create test user"""
        return User(
            id=user_id,
            name=f"User {user_id}",
            email=f"user{user_id}@example.com",
            wage=Money(50000, "ARS"),
            is_deleted=False,
            deleted_at=None
        )


class TestResponsibilityCalculatorCustomSplit:
    """Tests para split CUSTOM"""

    def test_calculate_custom_split_valid_percentages(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2)]
        custom_percentages = {1: Decimal("70"), 2: Decimal("30")}
        amount = Money(10000, "ARS")

        responsibilities = calculator.calculate_responsibilities(
            expense_id=1,
            budget_id=1,
            amount=amount,
            split_type=SplitType.CUSTOM,
            participants=users,
            period=Period(2026, 1),
            custom_percentages=custom_percentages
        )

        assert len(responsibilities) == 2

        resp1 = next(r for r in responsibilities if r.user_id == 1)
        resp2 = next(r for r in responsibilities if r.user_id == 2)

        assert resp1.percentage == Decimal("70")
        assert resp2.percentage == Decimal("30")

        assert resp1.responsible_amount == Money(7000, "ARS")
        assert resp2.responsible_amount == Money(3000, "ARS")

    def test_calculate_custom_split_missing_percentages(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2)]
        custom_percentages = {1: Decimal("100")}  # Missing user 2
        amount = Money(10000, "ARS")

        with pytest.raises(InvalidCalculation) as err_desc:
            calculator.calculate_responsibilities(
                expense_id=1,
                budget_id=1,
                amount=amount,
                split_type=SplitType.CUSTOM,
                participants=users,
                period=Period(2026, 1),
                custom_percentages=custom_percentages
            )

        assert "Missing:" in str(err_desc.value)

    def test_calculate_custom_split_extra_percentages(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1)]
        custom_percentages = {1: Decimal("50"), 2: Decimal("50")}  # Extra user 2
        amount = Money(10000, "ARS")

        with pytest.raises(InvalidCalculation) as err_desc:
            calculator.calculate_responsibilities(
                expense_id=1,
                budget_id=1,
                amount=amount,
                split_type=SplitType.CUSTOM,
                participants=users,
                period=Period(2026, 1),
                custom_percentages=custom_percentages
            )

        assert "Extra:" in str(err_desc.value)

    def test_calculate_custom_split_percentages_not_100(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2)]
        custom_percentages = {1: Decimal("60"), 2: Decimal("30")}  # Sum to 90
        amount = Money(10000, "ARS")

        with pytest.raises(InvalidCalculation) as err_desc:
            calculator.calculate_responsibilities(
                expense_id=1,
                budget_id=1,
                amount=amount,
                split_type=SplitType.CUSTOM,
                participants=users,
                period=Period(2026, 1),
                custom_percentages=custom_percentages
            )

        assert "sum to 100%" in str(err_desc.value)

    def _create_user(self, user_id: int) -> User:
        """Helper to create test user"""
        return User(
            id=user_id,
            name=f"User {user_id}",
            email=f"user{user_id}@example.com",
            wage=Money(50000, "ARS"),
            is_deleted=False,
            deleted_at=None
        )


class TestResponsibilityCalculatorFullSingleSplit:
    """Tests para split FULL_SINGLE"""

    def test_calculate_full_single_split_valid_user(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2)]
        amount = Money(10000, "ARS")

        responsibilities = calculator.calculate_responsibilities(
            expense_id=1,
            budget_id=1,
            amount=amount,
            split_type=SplitType.FULL_SINGLE,
            participants=users,
            period=Period(2026, 1),
            full_single_user_id=1
        )

        assert len(responsibilities) == 2

        resp1 = next(r for r in responsibilities if r.user_id == 1)
        resp2 = next(r for r in responsibilities if r.user_id == 2)

        assert resp1.percentage == Decimal("100")
        assert resp2.percentage == Decimal("0")

        assert resp1.responsible_amount == Money(10000, "ARS")
        assert resp2.responsible_amount == Money(0, "ARS")

    def test_calculate_full_single_split_missing_user_id(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2)]
        amount = Money(10000, "ARS")

        with pytest.raises(InvalidCalculation) as err_desc:
            calculator.calculate_responsibilities(
                expense_id=1,
                budget_id=1,
                amount=amount,
                split_type=SplitType.FULL_SINGLE,
                participants=users,
                period=Period(2026, 1),
                full_single_user_id=None
            )

        assert "full_single_user_id is required" in str(err_desc.value)

    def test_calculate_full_single_split_user_not_participant(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1), self._create_user(2)]
        amount = Money(10000, "ARS")

        with pytest.raises(InvalidCalculation) as err_desc:
            calculator.calculate_responsibilities(
                expense_id=1,
                budget_id=1,
                amount=amount,
                split_type=SplitType.FULL_SINGLE,
                participants=users,
                period=Period(2026, 1),
                full_single_user_id=3  # Not a participant
            )

        assert "not a participant" in str(err_desc.value)

    def _create_user(self, user_id: int) -> User:
        """Helper to create test user"""
        return User(
            id=user_id,
            name=f"User {user_id}",
            email=f"user{user_id}@example.com",
            wage=Money(50000, "ARS"),
            is_deleted=False,
            deleted_at=None
        )


class TestResponsibilityCalculatorGeneral:
    """Tests generales"""

    def test_calculate_responsibilities_no_participants(self):
        calculator = ResponsibilityCalculator()
        amount = Money(10000, "ARS")

        with pytest.raises(InvalidCalculation) as err_desc:
            calculator.calculate_responsibilities(
                expense_id=1,
                budget_id=1,
                amount=amount,
                split_type=SplitType.EQUAL,
                participants=[],
                period=Period(2026, 1)
            )

        assert "At least one participant" in str(err_desc.value)

    def test_calculate_responsibilities_unsupported_split_type(self):
        calculator = ResponsibilityCalculator()
        users = [self._create_user(1)]
        amount = Money(10000, "ARS")

        # Mock an invalid split type
        invalid_split_type = Mock()
        invalid_split_type.__str__ = Mock(return_value="INVALID")

        with pytest.raises(InvalidCalculation) as err_desc:
            calculator.calculate_responsibilities(
                expense_id=1,
                budget_id=1,
                amount=amount,
                split_type=invalid_split_type,
                participants=users,
                period=Period(2026, 1)
            )

        assert "Unsupported split type" in str(err_desc.value)

    def _create_user(self, user_id: int) -> User:
        """Helper to create test user"""
        return User(
            id=user_id,
            name=f"User {user_id}",
            email=f"user{user_id}@example.com",
            wage=Money(50000, "ARS"),
            is_deleted=False,
            deleted_at=None
        )