# backend/tests/unit/domain/test_monthly_budget.py
import pytest
from datetime import datetime
from app.domain.entities.monthly_budget import MonthlyBudget
from app.domain.value_objects.period import Period
from app.domain.value_objects.budget_status import BudgetStatus
from app.domain.exceptions.domain_exceptions import InvalidEntity


class TestMonthlyBudgetCreation:
    """Tests de creación de MonthlyBudget"""

    def test_should_create_budget_with_valid_data(self):
        period = Period(2026, 1)
        created_at = datetime(2026, 1, 12, 10, 0, 0)

        budget = MonthlyBudget(
            id=1,
            name="Presupuesto Hogar",
            period=period,
            description="Gastos comunes del hogar",
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=created_at,
            updated_at=None
        )

        assert budget.id == 1
        assert budget.name == "Presupuesto Hogar"
        assert budget.period == period
        assert budget.description == "Gastos comunes del hogar"
        assert budget.status == BudgetStatus.ACTIVE
        assert budget.created_by_user_id == 1
        assert budget.created_at == created_at
        assert budget.updated_at is None

    def test_should_create_budget_with_none_id(self):
        period = Period(2026, 1)
        created_at = datetime(2026, 1, 12, 10, 0, 0)

        budget = MonthlyBudget(
            id=None,
            name="Nuevo Presupuesto",
            period=period,
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=created_at,
            updated_at=None
        )

        assert budget.id is None
        assert budget.description is None

    def test_should_raise_exception_when_name_is_empty(self):
        period = Period(2026, 1)
        created_at = datetime(2026, 1, 12, 10, 0, 0)

        with pytest.raises(InvalidEntity) as err_desc:
            MonthlyBudget(
                id=1,
                name="",
                period=period,
                description=None,
                status=BudgetStatus.ACTIVE,
                created_by_user_id=1,
                created_at=created_at,
                updated_at=None
            )

        assert "name cannot be empty" in str(err_desc.value).lower()

    def test_should_raise_exception_when_name_is_whitespace(self):
        period = Period(2026, 1)
        created_at = datetime(2026, 1, 12, 10, 0, 0)

        with pytest.raises(InvalidEntity) as err_desc:
            MonthlyBudget(
                id=1,
                name="   ",
                period=period,
                description=None,
                status=BudgetStatus.ACTIVE,
                created_by_user_id=1,
                created_at=created_at,
                updated_at=None
            )

        assert "name cannot be empty" in str(err_desc.value).lower()

    def test_should_raise_exception_when_created_by_user_id_is_zero(self):
        period = Period(2026, 1)
        created_at = datetime(2026, 1, 12, 10, 0, 0)

        with pytest.raises(InvalidEntity) as err_desc:
            MonthlyBudget(
                id=1,
                name="Presupuesto",
                period=period,
                description=None,
                status=BudgetStatus.ACTIVE,
                created_by_user_id=0,
                created_at=created_at,
                updated_at=None
            )

        assert "created_by_user_id must be positive" in str(err_desc.value).lower()

    def test_should_raise_exception_when_created_by_user_id_is_negative(self):
        period = Period(2026, 1)
        created_at = datetime(2026, 1, 12, 10, 0, 0)

        with pytest.raises(InvalidEntity) as err_desc:
            MonthlyBudget(
                id=1,
                name="Presupuesto",
                period=period,
                description=None,
                status=BudgetStatus.ACTIVE,
                created_by_user_id=-1,
                created_at=created_at,
                updated_at=None
            )

        assert "created_by_user_id must be positive" in str(err_desc.value).lower()


class TestMonthlyBudgetMethods:
    """Tests de métodos de MonthlyBudget"""

    def test_should_return_string_representation(self):
        period = Period(2026, 1)
        created_at = datetime(2026, 1, 12, 10, 0, 0)

        budget = MonthlyBudget(
            id=1,
            name="Presupuesto Hogar",
            period=period,
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=created_at,
            updated_at=None
        )

        expected = "MonthlyBudget(Presupuesto Hogar, Period(year=2026, month=1), active)"
        assert str(budget) == expected

    def test_is_active_should_return_true_for_active_budget(self):
        period = Period(2026, 1)
        created_at = datetime(2026, 1, 12, 10, 0, 0)

        budget = MonthlyBudget(
            id=1,
            name="Presupuesto",
            period=period,
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=created_at,
            updated_at=None
        )

        assert budget.is_active() is True

    def test_is_active_should_return_false_for_closed_budget(self):
        period = Period(2026, 1)
        created_at = datetime(2026, 1, 12, 10, 0, 0)

        budget = MonthlyBudget(
            id=1,
            name="Presupuesto",
            period=period,
            description=None,
            status=BudgetStatus.CLOSED,
            created_by_user_id=1,
            created_at=created_at,
            updated_at=None
        )

        assert budget.is_active() is False

    def test_can_be_edited_should_return_true_for_active_budget(self):
        period = Period(2026, 1)
        created_at = datetime(2026, 1, 12, 10, 0, 0)

        budget = MonthlyBudget(
            id=1,
            name="Presupuesto",
            period=period,
            description=None,
            status=BudgetStatus.ACTIVE,
            created_by_user_id=1,
            created_at=created_at,
            updated_at=None
        )

        assert budget.can_be_edited() is True

    def test_can_be_edited_should_return_false_for_closed_budget(self):
        period = Period(2026, 1)
        created_at = datetime(2026, 1, 12, 10, 0, 0)

        budget = MonthlyBudget(
            id=1,
            name="Presupuesto",
            period=period,
            description=None,
            status=BudgetStatus.CLOSED,
            created_by_user_id=1,
            created_at=created_at,
            updated_at=None
        )

        assert budget.can_be_edited() is False