import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from decimal import Decimal

from app.domain.entities.credit_card import CreditCard
from app.domain.value_objects.money import Money, Currency
from app.infrastructure.persistence.models.credit_card_model import CreditCardModel
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.repositories.sqlalchemy_credit_card_repository import (
    SQLAlchemyCreditCardRepository,
)


@pytest.fixture
def db_session():
    """In-memory SQLite for tests"""
    engine = create_engine("sqlite:///:memory:")
    UserModel.metadata.create_all(engine)
    CreditCardModel.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create test user
    test_user = UserModel(
        id=1,
        name="Test User",
        email="test@example.com",
        wage_amount=50000,
        wage_currency="ARS",
        is_deleted=False,
    )
    session.add(test_user)
    session.commit()

    yield session
    session.close()


@pytest.fixture
def credit_card_repository(db_session: Session):
    return SQLAlchemyCreditCardRepository(db_session)


class TestSQLAlchemyCreditCardRepositorySave:
    def test_should_save_new_credit_card(self, credit_card_repository):
        # Arrange
        new_card = CreditCard(
            id=None,
            user_id=1,
            name="Visa Gold",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
            credit_limit=Money(Decimal("100000.00"), Currency.ARS),
        )

        # Act
        saved_card = credit_card_repository.save(new_card)

        # Assert
        assert saved_card.id is not None
        assert saved_card.user_id == 1
        assert saved_card.name == "Visa Gold"
        assert saved_card.bank == "HSBC"
        assert saved_card.last_four_digits == "1234"
        assert saved_card.billing_close_day == 10
        assert saved_card.payment_due_day == 20
        assert saved_card.credit_limit.amount == Decimal("100000.00")
        assert saved_card.credit_limit.currency == Currency.ARS

        # Verify in DB
        retrieved = credit_card_repository.find_by_id(saved_card.id)
        assert retrieved == saved_card

    def test_should_save_credit_card_without_limit(self, credit_card_repository):
        # Arrange
        new_card = CreditCard(
            id=None,
            user_id=1,
            name="Visa Basic",
            bank="Santander",
            last_four_digits="5678",
            billing_close_day=15,
            payment_due_day=25,
            credit_limit=None,
        )

        # Act
        saved_card = credit_card_repository.save(new_card)

        # Assert
        assert saved_card.id is not None
        assert saved_card.credit_limit is None

    def test_should_update_existing_credit_card(self, credit_card_repository):
        # Arrange - Create and save
        card = CreditCard(
            id=None,
            user_id=1,
            name="Mastercard",
            bank="Galicia",
            last_four_digits="9999",
            billing_close_day=10,
            payment_due_day=20,
            credit_limit=Money(Decimal("50000.00"), Currency.ARS),
        )
        saved = credit_card_repository.save(card)
        original_id = saved.id

        # Act - Update
        updated_card = CreditCard(
            id=original_id,
            user_id=1,
            name="Mastercard Platinum",
            bank="Galicia",
            last_four_digits="9999",
            billing_close_day=10,
            payment_due_day=20,
            credit_limit=Money(Decimal("150000.00"), Currency.ARS),
        )
        updated = credit_card_repository.save(updated_card)

        # Assert
        assert updated.id == original_id
        assert updated.name == "Mastercard Platinum"
        assert updated.credit_limit.amount == Decimal("150000.00")

        # Verify in DB
        from_db = credit_card_repository.find_by_id(original_id)
        assert from_db.name == "Mastercard Platinum"


class TestSQLAlchemyCreditCardRepositoryFindById:
    def test_should_find_existing_credit_card(self, credit_card_repository):
        # Arrange
        card = CreditCard(
            id=None,
            user_id=1,
            name="Amex",
            bank="American Express",
            last_four_digits="4444",
            billing_close_day=5,
            payment_due_day=15,
        )
        saved = credit_card_repository.save(card)

        # Act
        found = credit_card_repository.find_by_id(saved.id)

        # Assert
        assert found is not None
        assert found.id == saved.id
        assert found.name == "Amex"

    def test_should_return_none_for_nonexistent_id(self, credit_card_repository):
        # Act
        found = credit_card_repository.find_by_id(999)

        # Assert
        assert found is None


class TestSQLAlchemyCreditCardRepositoryFindByUserId:
    def test_should_return_all_cards_for_user(self, credit_card_repository):
        # Arrange
        card1 = CreditCard(
            id=None,
            user_id=1,
            name="Card 1",
            bank="Bank 1",
            last_four_digits="1111",
            billing_close_day=10,
            payment_due_day=20,
        )
        card2 = CreditCard(
            id=None,
            user_id=1,
            name="Card 2",
            bank="Bank 2",
            last_four_digits="2222",
            billing_close_day=15,
            payment_due_day=25,
        )
        card3 = CreditCard(
            id=None,
            user_id=1,
            name="Card 3",
            bank="Bank 3",
            last_four_digits="3333",
            billing_close_day=20,
            payment_due_day=30,
        )

        credit_card_repository.save(card1)
        credit_card_repository.save(card2)
        credit_card_repository.save(card3)

        # Act
        user_cards = credit_card_repository.find_by_user_id(1)

        # Assert
        assert len(user_cards) == 3
        names = [c.name for c in user_cards]
        assert "Card 1" in names
        assert "Card 2" in names
        assert "Card 3" in names

    def test_should_return_empty_list_for_user_without_cards(
        self, credit_card_repository
    ):
        # Act
        user_cards = credit_card_repository.find_by_user_id(999)

        # Assert
        assert user_cards == []
