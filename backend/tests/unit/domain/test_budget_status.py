# backend/tests/unit/domain/test_budget_status.py
import pytest
from app.domain.value_objects.budget_status import BudgetStatus


class TestBudgetStatus:
    """Tests para BudgetStatus enum"""

    def test_should_have_all_expected_values(self):
        expected_values = {"active", "closed", "archived"}
        actual_values = {member.value for member in BudgetStatus}
        assert actual_values == expected_values

    def test_should_be_string_enum(self):
        assert isinstance(BudgetStatus.ACTIVE, str)
        assert BudgetStatus.ACTIVE == "active"
        assert BudgetStatus.CLOSED == "closed"
        assert BudgetStatus.ARCHIVED == "archived"