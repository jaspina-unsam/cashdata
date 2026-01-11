from app.domain.entities.bank_account import BankAccount
from app.domain.value_objects.money import Currency
from app.infrastructure.persistence.models.bank_account_model import BankAccountModel


class BankAccountMapper:
    @staticmethod
    def to_entity(model: BankAccountModel) -> BankAccount:
        return BankAccount(
            id=model.id,
            payment_method_id=model.payment_method_id,
            primary_user_id=model.primary_user_id,
            secondary_user_id=model.secondary_user_id,
            name=model.name,
            bank=model.bank,
            account_type=model.account_type,
            last_four_digits=model.last_four_digits,
            currency=Currency(model.currency),
        )

    @staticmethod
    def to_model(entity: BankAccount) -> BankAccountModel:
        model = BankAccountModel(
            id=entity.id,
            payment_method_id=entity.payment_method_id,
            primary_user_id=entity.primary_user_id,
            secondary_user_id=entity.secondary_user_id,
            name=entity.name,
            bank=entity.bank,
            account_type=entity.account_type,
            last_four_digits=entity.last_four_digits,
            currency=entity.currency.value,
        )
        return model
