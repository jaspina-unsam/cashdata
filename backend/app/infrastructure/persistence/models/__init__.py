from sqlalchemy.orm import declarative_base
from app.infrastructure.persistence.models.base import Base
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.models.monthly_income_model import (
    MonthlyIncomeModel,
)
from app.infrastructure.persistence.models.category_model import CategoryModel
from app.infrastructure.persistence.models.credit_card_model import CreditCardModel
from app.infrastructure.persistence.models.purchase_model import PurchaseModel
from app.infrastructure.persistence.models.installment_model import InstallmentModel
from app.infrastructure.persistence.models.payment_method_model import PaymentMethodModel
from app.infrastructure.persistence.models.cash_account_model import CashAccountModel
from app.infrastructure.persistence.models.bank_account_model import BankAccountModel

__all__ = [
    "Base",
    "UserModel",
    "MonthlyIncomeModel",
    "CategoryModel",
    "CreditCardModel",
    "PurchaseModel",
    "InstallmentModel",
    "PaymentMethodModel",
    "CashAccountModel",
    "BankAccountModel",
    "MonthlyStatementModel",
]