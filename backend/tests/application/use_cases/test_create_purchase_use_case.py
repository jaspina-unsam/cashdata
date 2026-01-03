import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cashdata.application.use_cases.create_purchase_use_case import (
    CreatePurchaseUseCase,
    CreatePurchaseCommand,
)
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.infrastructure.persistence.models.user_model import UserModel
from cashdata.infrastructure.persistence.models.category_model import CategoryModel
from cashdata.infrastructure.persistence.models.credit_card_model import CreditCardModel
from cashdata.infrastructure.persistence.models.purchase_model import PurchaseModel
from cashdata.infrastructure.persistence.models.installment_model import InstallmentModel
from cashdata.infrastructure.persistence.repositories.sqlalchemy_unit_of_work import (
    SQLAlchemyUnitOfWork,
)


@pytest.fixture
def session_factory():
    """Create in-memory SQLite database"""
    engine = create_engine("sqlite:///:memory:")
    UserModel.metadata.create_all(engine)
    CategoryModel.metadata.create_all(engine)
    CreditCardModel.metadata.create_all(engine)
    PurchaseModel.metadata.create_all(engine)
    InstallmentModel.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine)
    
    # Create test data
    session = SessionFactory()
    test_user = UserModel(
        id=1, name="Test User", email="test@example.com",
        wage_amount=100000, wage_currency="ARS", is_deleted=False
    )
    test_category = CategoryModel(id=1, name="Electronics", color="#FF5733", icon="laptop")
    test_card = CreditCardModel(
        id=1, user_id=1, name="Visa", bank="HSBC",
        last_four_digits="1234", billing_close_day=10, payment_due_day=20
    )
    session.add_all([test_user, test_category, test_card])
    session.commit()
    session.close()
    
    yield SessionFactory


@pytest.fixture
def use_case(session_factory):
    """Create use case with real UnitOfWork"""
    return CreatePurchaseUseCase(SQLAlchemyUnitOfWork(session_factory))


class TestCreatePurchaseUseCaseIntegration:
    """
    Integration tests for CreatePurchaseUseCase with real database.
    
    Purpose: Validate the complete flow including database operations,
    installment generation, and transaction management.
    """
    
    def test_creates_purchase_with_single_installment_successfully(self, use_case, session_factory):
        """
        GIVEN: Valid purchase command with 1 installment
        WHEN: Execute use case
        THEN: Purchase and installment are persisted in database
        """
        # Arrange
        command = CreatePurchaseCommand(
            user_id=1,
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Laptop",
            total_amount=Decimal("50000.00"),
            currency=Currency.ARS,
            installments_count=1
        )
        
        # Act
        result = use_case.execute(command)
        
        # Assert
        assert result.purchase_id is not None
        assert result.installments_count == 1
        
        # Verify data in database
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            purchase = uow.purchases.find_by_id(result.purchase_id)
            installments = uow.installments.find_by_purchase_id(result.purchase_id)
            
        assert purchase is not None
        assert purchase.description == "Laptop"
        assert purchase.total_amount.amount == Decimal("50000.00")
        assert len(installments) == 1
        assert installments[0].amount.amount == Decimal("50000.00")
    
    def test_creates_purchase_with_multiple_installments_successfully(self, use_case, session_factory):
        """
        GIVEN: Valid purchase command with 12 installments
        WHEN: Execute use case
        THEN: Purchase and 12 installments are persisted with correct amounts
        """
        # Arrange
        command = CreatePurchaseCommand(
            user_id=1,
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="TV 4K",
            total_amount=Decimal("120000.00"),
            currency=Currency.ARS,
            installments_count=12
        )
        
        # Act
        result = use_case.execute(command)
        
        # Assert
        assert result.installments_count == 12
        
        # Verify installments in database
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            purchase = uow.purchases.find_by_id(result.purchase_id)
            installments = uow.installments.find_by_purchase_id(result.purchase_id)
            
        assert len(installments) == 12
        
        # Verify amount distribution (120000 / 12 = 10000 each)
        total_from_installments = sum(inst.amount.amount for inst in installments)
        assert total_from_installments == Decimal("120000.00")
        assert all(inst.amount.amount == Decimal("10000.00") for inst in installments)
    
    def test_creates_purchase_with_uneven_division(self, use_case, session_factory):
        """
        GIVEN: Purchase with amount that doesn't divide evenly
        WHEN: Execute use case
        THEN: First installment absorbs remainder
        """
        # Arrange
        command = CreatePurchaseCommand(
            user_id=1,
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Phone",
            total_amount=Decimal("10000.00"),
            currency=Currency.ARS,
            installments_count=3
        )
        
        # Act
        result = use_case.execute(command)
        
        # Assert
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            installments = uow.installments.find_by_purchase_id(result.purchase_id)
            
        assert len(installments) == 3
        # 10000 / 3 = 3333.33 per installment (rounded to cents)
        # First installment: 3333.33 + 0.01 remainder = 3333.34
        assert installments[0].amount.amount == Decimal("3333.34")
        assert installments[1].amount.amount == Decimal("3333.33")
        assert installments[2].amount.amount == Decimal("3333.33")
        
        # Verify total
        total = sum(inst.amount.amount for inst in installments)
        assert total == Decimal("10000.00")
    
    def test_raises_error_when_credit_card_not_found(self, use_case):
        """
        GIVEN: Command with non-existent credit card
        WHEN: Execute use case
        THEN: Raises ValueError and nothing is persisted
        """
        # Arrange
        command = CreatePurchaseCommand(
            user_id=1,
            credit_card_id=999,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Should fail",
            total_amount=Decimal("1000.00"),
            currency=Currency.ARS,
            installments_count=1
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Credit card with ID 999 not found"):
            use_case.execute(command)
    
    def test_raises_error_when_credit_card_belongs_to_different_user(self, use_case, session_factory):
        """
        GIVEN: Credit card belonging to different user
        WHEN: Execute use case
        THEN: Raises ValueError
        """
        # Create another user and credit card
        session = session_factory()
        other_user = UserModel(
            id=2, name="Other User", email="other@example.com",
            wage_amount=50000, wage_currency="ARS", is_deleted=False
        )
        other_card = CreditCardModel(
            id=2, user_id=2, name="MasterCard", bank="Santander",
            last_four_digits="5678", billing_close_day=15, payment_due_day=25
        )
        session.add_all([other_user, other_card])
        session.commit()
        session.close()
        
        # Arrange
        command = CreatePurchaseCommand(
            user_id=1,  # User 1 trying to use card from user 2
            credit_card_id=2,
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Should fail",
            total_amount=Decimal("1000.00"),
            currency=Currency.ARS,
            installments_count=1
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="does not belong to user 1"):
            use_case.execute(command)
    
    def test_raises_error_when_category_not_found(self, use_case):
        """
        GIVEN: Command with non-existent category
        WHEN: Execute use case
        THEN: Raises ValueError
        """
        # Arrange
        command = CreatePurchaseCommand(
            user_id=1,
            credit_card_id=1,
            category_id=999,
            purchase_date=date(2025, 1, 15),
            description="Should fail",
            total_amount=Decimal("1000.00"),
            currency=Currency.ARS,
            installments_count=1
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Category with ID 999 not found"):
            use_case.execute(command)
    
    def test_installments_have_correct_billing_periods(self, use_case, session_factory):
        """
        GIVEN: Purchase on 2025-01-15 with card closing day 10, due day 20
        WHEN: Execute use case with 3 installments
        THEN: Installments have correct sequential billing periods based on due_date - 1
        
        Purchase on Jan 15 (after close day 10):
        - Inst 1: closes Feb 10, dues Feb 20 → period = Jan (202501)
        - Inst 2: closes Mar 10, dues Mar 20 → period = Feb (202502)
        - Inst 3: closes Apr 10, dues Apr 20 → period = Mar (202503)
        """
        # Arrange
        command = CreatePurchaseCommand(
            user_id=1,
            credit_card_id=1,
            category_id=1,
            purchase_date=date(2025, 1, 15),  # After closing day 10
            description="Multi-month purchase",
            total_amount=Decimal("30000.00"),
            currency=Currency.ARS,
            installments_count=3
        )
        
        # Act
        result = use_case.execute(command)
        
        # Assert
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            installments = uow.installments.find_by_purchase_id(result.purchase_id)
            
        # Billing period = month of due_date minus 1
        assert installments[0].billing_period == "202501"  # Due Feb 20 → Jan
        assert installments[1].billing_period == "202502"  # Due Mar 20 → Feb
        assert installments[2].billing_period == "202503"  # Due Apr 20 → Mar
    
    def test_transaction_rollback_on_error(self, use_case, session_factory):
        """
        GIVEN: Purchase that will fail validation
        WHEN: Execute use case
        THEN: No data is persisted (transaction rolled back)
        """
        # Arrange
        command = CreatePurchaseCommand(
            user_id=1,
            credit_card_id=999,  # Invalid card
            category_id=1,
            purchase_date=date(2025, 1, 15),
            description="Should rollback",
            total_amount=Decimal("5000.00"),
            currency=Currency.ARS,
            installments_count=1
        )
        
        # Act
        try:
            use_case.execute(command)
        except ValueError:
            pass
        
        # Assert - Verify nothing was persisted
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            purchases = uow.purchases.find_by_user_id(1)
            
        assert len(purchases) == 0  # No purchases created
