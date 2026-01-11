from app.domain.entities.cash_account import CashAccount
from app.domain.value_objects.money import Currency
from app.infrastructure.persistence.models.cash_account_model import CashAccountModel


class CashAccountMapper:
    @staticmethod
    def to_entity(model: CashAccountModel) -> CashAccount:
        return CashAccount(
            id=model.id,
            payment_method_id=model.payment_method_id,
            user_id=model.user_id,
            name=model.name,
            currency=Currency(model.currency),
        )

    @staticmethod
    def to_model(entity: CashAccount) -> CashAccountModel:
        model = CashAccountModel(
            id=entity.id,
            payment_method_id=entity.payment_method_id,
            user_id=entity.user_id,
            name=entity.name,
            currency=entity.currency.value,
        )
        return model
