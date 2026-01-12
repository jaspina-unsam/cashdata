# backend/tests/unit/domain/test_split_type.py
import pytest
from app.domain.value_objects.split_type import SplitType


class TestSplitType:
    """Tests para SplitType enum"""

    def test_should_have_all_expected_values(self):
        expected_values = {"equal", "proportional", "custom", "full_single"}
        actual_values = {member.value for member in SplitType}
        assert actual_values == expected_values

    def test_should_be_string_enum(self):
        assert isinstance(SplitType.EQUAL, str)
        assert SplitType.EQUAL == "equal"
        assert SplitType.PROPORTIONAL == "proportional"
        assert SplitType.CUSTOM == "custom"
        assert SplitType.FULL_SINGLE == "full_single"