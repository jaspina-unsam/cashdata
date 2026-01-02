from decimal import Decimal
from typing import Optional

from cashdata.domain.entities.tarjeta_credito import CreditCard
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.infrastructure.persistence.models.credit_card_model import CreditCardModel


class CreditCardMapper:
    @staticmethod
    def to_entity(model: CreditCardModel) -> CreditCard:
        """SQLAlchemy Model → Domain Entity"""
        credit_limit = None
        if model.credit_limit_amount is not None and model.credit_limit_currency is not None:
            credit_limit = Money(
                Decimal(str(model.credit_limit_amount)),
                Currency(model.credit_limit_currency),
            )

        return CreditCard(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            bank=model.bank,
            last_four_digits=model.last_four_digits,
            billing_close_day=model.billing_close_day,
            payment_due_day=model.payment_due_day,
            credit_limit=credit_limit,
        )

    @staticmethod
    def to_model(entity: CreditCard) -> CreditCardModel:
        """Domain Entity → SQLAlchemy Model"""
        credit_limit_amount = None
        credit_limit_currency = None
        if entity.credit_limit is not None:
            credit_limit_amount = float(entity.credit_limit.amount)
            # Currency is StrEnum, so it can be used directly as a string
            credit_limit_currency = entity.credit_limit.currency

        return CreditCardModel(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            bank=entity.bank,
            last_four_digits=entity.last_four_digits,
            billing_close_day=entity.billing_close_day,
            payment_due_day=entity.payment_due_day,
            credit_limit_amount=credit_limit_amount,
            credit_limit_currency=credit_limit_currency,
        )
