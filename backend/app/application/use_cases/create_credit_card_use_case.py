from dataclasses import dataclass
from decimal import Decimal

from app.domain.entities.credit_card import CreditCard
from app.domain.entities.payment_method import PaymentMethod
from app.domain.repositories import IUnitOfWork
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.domain.value_objects.money import Money, Currency


@dataclass(frozen=True)
class CreateCreditCardQuery:
    """Query to create a new credit card"""

    user_id: int
    name: str
    bank: str
    last_four_digits: str
    billing_close_day: int
    payment_due_day: int
    credit_limit_amount: Decimal | None = None
    credit_limit_currency: Currency | None = None


class CreateCreditCardUseCase:
    """
    Use case to create a new credit card.

    Credit cards are payment methods that allow users to make purchases on credit.
    Creates both a PaymentMethod and CreditCard entity atomically.
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def execute(self, query: CreateCreditCardQuery) -> CreditCard:
        """
        Execute the use case to create a credit card.

        Args:
            query: The query containing credit card data

        Returns:
            Created CreditCard entity
        """
        # Create credit limit Money object if provided
        credit_limit = None
        if (
            query.credit_limit_amount is not None
            and query.credit_limit_currency is not None
        ):
            credit_limit = Money(query.credit_limit_amount, query.credit_limit_currency)

        with self.unit_of_work as uow:
            # First, create the PaymentMethod entity
            payment_method = uow.payment_methods.save(
                PaymentMethod(
                    id=None,
                    user_id=query.user_id,
                    type=PaymentMethodType.CREDIT_CARD,
                    name=query.name,
                )
            )

            # Then, create the CreditCard entity
            credit_card = CreditCard(
                id=None,
                payment_method_id=payment_method.id,
                user_id=query.user_id,
                name=query.name,
                bank=query.bank,
                last_four_digits=query.last_four_digits,
                billing_close_day=query.billing_close_day,
                payment_due_day=query.payment_due_day,
                credit_limit=credit_limit,
            )

            saved_credit_card = uow.credit_cards.save(credit_card)
            uow.commit()

            return saved_credit_card
