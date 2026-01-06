# tests/application/mappers/test_user_dto_mapper.py
import json
from decimal import Decimal
import pytest
from app.domain.value_objects.money import Money, Currency
from app.domain.entities.user import User
from app.infrastructure.persistence.mappers.user_dto_mapper import UserDTOMapper
from app.application.dtos.user_dto import UserResponseDTO


@pytest.fixture
def make_user():
    def _make(id, name, email, wage_amount, wage_currency=Currency.ARS):
        return User(
            id, name, email, wage=Money(Decimal(str(wage_amount)), wage_currency)
        )

    return _make


class TestUserDTOMapper:
    def test_to_response_dto_maps_correctly(self, make_user):
        """GIVEN User entity, WHEN map to DTO, THEN all fields correct"""
        test_user = make_user(1, "Test", "test@mail.com", 1200000)
        mapped_user = UserDTOMapper.to_response_dto(test_user)

        assert mapped_user.id == 1
        assert mapped_user.name == "Test"
        assert mapped_user.email == "test@mail.com"
        assert mapped_user.wage_amount == Decimal("1200000")
        assert mapped_user.wage_currency == Currency.ARS


def test_user_response_dto_serializes_correctly():
    """
    GIVEN: UserResponseDTO with Decimal and Enum
    WHEN: Serialize to JSON
    THEN: Decimal becomes string, Enum becomes value
    """
    dto = UserResponseDTO(
        id=1,
        name="Juan",
        email="juan@mail.com",
        wage_amount=Decimal("50000.50"),
        wage_currency=Currency.ARS,
    )

    # Test model_dump (Python dict)
    data = dto.model_dump()
    assert isinstance(data["wage_amount"], Decimal)
    assert data["wage_currency"] == "ARS"

    # Test model_dump_json (JSON string)
    json_str = dto.model_dump_json()
    parsed = json.loads(json_str)
    assert parsed["wage_amount"] == "50000.50"
    assert parsed["wage_currency"] == "ARS"


def test_user_response_dto_from_entity(make_user):
    """
    GIVEN: User entity with Money value object
    WHEN: Map to DTO
    THEN: Correctly flattens to primitives
    """
    user = make_user(1, "Olga", "olga@mail.com", 650000)

    dto = UserResponseDTO(
        id=user.id,
        name=user.name,
        email=user.email,
        wage_amount=user.wage.amount,
        wage_currency=user.wage.currency,
    )

    assert dto.wage_amount == Decimal("650000")
    assert dto.wage_currency == "ARS"
