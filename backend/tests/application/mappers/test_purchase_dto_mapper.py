import pytest
from datetime import date
from decimal import Decimal

from app.domain.entities.purchase import Purchase
from app.domain.entities.installment import Installment
from app.domain.entities.credit_card import CreditCard
from app.domain.entities.category import Category
from app.domain.value_objects.money import Money, Currency
from app.application.use_cases.get_credit_card_summary_use_case import (
    CreditCardSummary,
)
from app.application.mappers.purchase_dto_mapper import (
    PurchaseDTOMapper,
    InstallmentDTOMapper,
    CreditCardDTOMapper,
    CategoryDTOMapper,
    CreditCardSummaryDTOMapper,
)
from app.application.dtos.purchase_dto import (
    PurchaseResponseDTO,
    InstallmentResponseDTO,
    CreditCardResponseDTO,
    CategoryResponseDTO,
    CreditCardSummaryResponseDTO,
)


class TestPurchaseDTOMapper:

    def test_to_response_dto_maps_all_fields_correctly(self):
        """
        GIVEN: Purchase entity
        WHEN: Map to response DTO
        THEN: All fields are correctly mapped and Money is flattened
        """
        # Arrange
        purchase = Purchase(
            id=1,
            user_id=10,
            credit_card_id=1,
            category_id=2,
            purchase_date=date(2025, 1, 15),
            description="Laptop",
            total_amount=Money(Decimal("120000.00"), Currency.ARS),
            installments_count=12,
        )

        # Act
        dto = PurchaseDTOMapper.to_response_dto(purchase)

        # Assert
        assert isinstance(dto, PurchaseResponseDTO)
        assert dto.id == 1
        assert dto.user_id == 10
        assert dto.credit_card_id == 1
        assert dto.category_id == 2
        assert dto.purchase_date == date(2025, 1, 15)
        assert dto.description == "Laptop"
        assert dto.total_amount == Decimal("120000.00")
        assert dto.currency == Currency.ARS
        assert dto.installments_count == 12


class TestInstallmentDTOMapper:

    def test_to_response_dto_maps_all_fields_correctly(self):
        """
        GIVEN: Installment entity
        WHEN: Map to response DTO
        THEN: All fields are correctly mapped
        """
        # Arrange
        installment = Installment(
            id=1,
            purchase_id=1,
            installment_number=1,
            total_installments=12,
            amount=Money(Decimal("10000.00"), Currency.ARS),
            billing_period="202502",
            due_date=date(2025, 2, 20),
        )

        # Act
        dto = InstallmentDTOMapper.to_response_dto(installment)

        # Assert
        assert isinstance(dto, InstallmentResponseDTO)
        assert dto.id == 1
        assert dto.purchase_id == 1
        assert dto.installment_number == 1
        assert dto.total_installments == 12
        assert dto.amount == Decimal("10000.00")
        assert dto.currency == Currency.ARS
        assert dto.billing_period == "202502"
        assert dto.due_date == date(2025, 2, 20)


class TestCreditCardDTOMapper:

    def test_to_response_dto_with_credit_limit(self):
        """
        GIVEN: CreditCard entity with credit limit
        WHEN: Map to response DTO
        THEN: All fields including credit limit are mapped
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa Gold",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
            credit_limit=Money(Decimal("500000.00"), Currency.ARS),
        )

        # Act
        dto = CreditCardDTOMapper.to_response_dto(credit_card)

        # Assert
        assert isinstance(dto, CreditCardResponseDTO)
        assert dto.id == 1
        assert dto.user_id == 10
        assert dto.name == "Visa Gold"
        assert dto.bank == "HSBC"
        assert dto.last_four_digits == "1234"
        assert dto.billing_close_day == 10
        assert dto.payment_due_day == 20
        assert dto.credit_limit_amount == Decimal("500000.00")
        assert dto.credit_limit_currency == Currency.ARS

    def test_to_response_dto_without_credit_limit(self):
        """
        GIVEN: CreditCard entity without credit limit
        WHEN: Map to response DTO
        THEN: Credit limit fields are None
        """
        # Arrange
        credit_card = CreditCard(
            id=1,
            user_id=10,
            name="Visa",
            bank="HSBC",
            last_four_digits="1234",
            billing_close_day=10,
            payment_due_day=20,
            credit_limit=None,
        )

        # Act
        dto = CreditCardDTOMapper.to_response_dto(credit_card)

        # Assert
        assert dto.credit_limit_amount is None
        assert dto.credit_limit_currency is None


class TestCategoryDTOMapper:

    def test_to_response_dto_with_all_fields(self):
        """
        GIVEN: Category entity with all fields
        WHEN: Map to response DTO
        THEN: All fields are mapped
        """
        # Arrange
        category = Category(id=1, name="Electronics", color="#FF5733", icon="laptop")

        # Act
        dto = CategoryDTOMapper.to_response_dto(category)

        # Assert
        assert isinstance(dto, CategoryResponseDTO)
        assert dto.id == 1
        assert dto.name == "Electronics"
        assert dto.color == "#FF5733"
        assert dto.icon == "laptop"

    def test_to_response_dto_with_minimal_fields(self):
        """
        GIVEN: Category entity with only required fields
        WHEN: Map to response DTO
        THEN: Optional fields are None
        """
        # Arrange
        category = Category(id=1, name="Food", color=None, icon=None)

        # Act
        dto = CategoryDTOMapper.to_response_dto(category)

        # Assert
        assert dto.name == "Food"
        assert dto.color is None
        assert dto.icon is None


class TestCreditCardSummaryDTOMapper:

    def test_to_response_dto_with_installments(self):
        """
        GIVEN: CreditCardSummary with installments
        WHEN: Map to response DTO
        THEN: All fields including nested installments are mapped
        """
        # Arrange
        installments = [
            Installment(
                id=1,
                purchase_id=1,
                installment_number=1,
                total_installments=3,
                amount=Money(Decimal("1000.00"), Currency.ARS),
                billing_period="202501",
                due_date=date(2025, 2, 20),
            ),
            Installment(
                id=2,
                purchase_id=2,
                installment_number=1,
                total_installments=1,
                amount=Money(Decimal("2000.00"), Currency.ARS),
                billing_period="202501",
                due_date=date(2025, 2, 20),
            ),
        ]

        summary = CreditCardSummary(
            credit_card_id=1,
            billing_period="202501",
            total_amount=Money(Decimal("3000.00"), Currency.ARS),
            installments_count=2,
            installments=installments,
        )

        # Act
        dto = CreditCardSummaryDTOMapper.to_response_dto(summary)

        # Assert
        assert isinstance(dto, CreditCardSummaryResponseDTO)
        assert dto.credit_card_id == 1
        assert dto.billing_period == "202501"
        assert dto.total_amount == Decimal("3000.00")
        assert dto.currency == Currency.ARS
        assert dto.installments_count == 2
        assert len(dto.installments) == 2
        assert all(
            isinstance(inst, InstallmentResponseDTO) for inst in dto.installments
        )
