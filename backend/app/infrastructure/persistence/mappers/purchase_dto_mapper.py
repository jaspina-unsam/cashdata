from app.domain.entities.purchase import Purchase
from app.domain.entities.installment import Installment
from app.domain.entities.credit_card import CreditCard
from app.domain.entities.category import Category
from app.application.dtos.purchase_dto import (
    PurchaseResponseDTO,
    InstallmentResponseDTO,
    CreditCardResponseDTO,
    CategoryResponseDTO,
    CreditCardSummaryResponseDTO,
)
from app.application.use_cases.get_credit_card_summary_use_case import (
    CreditCardSummary,
)


class PurchaseDTOMapper:
    """Maps between Purchase entity and DTOs"""

    @staticmethod
    def to_response_dto(purchase: Purchase) -> PurchaseResponseDTO:
        """Convert Purchase entity to response DTO"""
        return PurchaseResponseDTO(
            id=purchase.id,
            user_id=purchase.user_id,
            credit_card_id=purchase.credit_card_id,
            category_id=purchase.category_id,
            purchase_date=purchase.purchase_date,
            description=purchase.description,
            total_amount=purchase.total_amount.amount,
            currency=purchase.total_amount.currency,
            installments_count=purchase.installments_count,
        )


class InstallmentDTOMapper:
    """Maps between Installment entity and DTOs"""

    @staticmethod
    def to_response_dto(installment: Installment) -> InstallmentResponseDTO:
        """Convert Installment entity to response DTO"""
        return InstallmentResponseDTO(
            id=installment.id,
            purchase_id=installment.purchase_id,
            installment_number=installment.installment_number,
            total_installments=installment.total_installments,
            amount=installment.amount.amount,
            currency=installment.amount.currency,
            billing_period=installment.billing_period,
            due_date=installment.due_date,
        )


class CreditCardDTOMapper:
    """Maps between CreditCard entity and DTOs"""

    @staticmethod
    def to_response_dto(credit_card: CreditCard) -> CreditCardResponseDTO:
        """Convert CreditCard entity to response DTO"""
        return CreditCardResponseDTO(
            id=credit_card.id,
            user_id=credit_card.user_id,
            name=credit_card.name,
            bank=credit_card.bank,
            last_four_digits=credit_card.last_four_digits,
            billing_close_day=credit_card.billing_close_day,
            payment_due_day=credit_card.payment_due_day,
            credit_limit_amount=(
                credit_card.credit_limit.amount if credit_card.credit_limit else None
            ),
            credit_limit_currency=(
                credit_card.credit_limit.currency if credit_card.credit_limit else None
            ),
        )


class CategoryDTOMapper:
    """Maps between Category entity and DTOs"""

    @staticmethod
    def to_response_dto(category: Category) -> CategoryResponseDTO:
        """Convert Category entity to response DTO"""
        return CategoryResponseDTO(
            id=category.id, name=category.name, color=category.color, icon=category.icon
        )


class CreditCardSummaryDTOMapper:
    """Maps between CreditCardSummary and DTOs"""

    @staticmethod
    def to_response_dto(summary: CreditCardSummary) -> CreditCardSummaryResponseDTO:
        """Convert CreditCardSummary to response DTO"""
        return CreditCardSummaryResponseDTO(
            credit_card_id=summary.credit_card_id,
            billing_period=summary.billing_period,
            total_amount=summary.total_amount.amount,
            currency=summary.total_amount.currency,
            installments_count=summary.installments_count,
            installments=[
                InstallmentDTOMapper.to_response_dto(inst)
                for inst in summary.installments
            ],
        )
