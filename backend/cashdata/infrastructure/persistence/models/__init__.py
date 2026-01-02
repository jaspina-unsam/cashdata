from sqlalchemy.orm import declarative_base
from cashdata.infrastructure.persistence.models.base import Base
from cashdata.infrastructure.persistence.models.user_model import UserModel
from cashdata.infrastructure.persistence.models.monthly_income_model import (
    MonthlyIncomeModel,
)
from cashdata.infrastructure.persistence.models.category_model import CategoryModel
from cashdata.infrastructure.persistence.models.credit_card_model import CreditCardModel
from cashdata.infrastructure.persistence.models.purchase_model import PurchaseModel
from cashdata.infrastructure.persistence.models.installment_model import InstallmentModel

__all__ = [
    "Base",
    "UserModel",
    "MonthlyIncomeModel",
    "CategoryModel",
    "CreditCardModel",
    "PurchaseModel",
    "InstallmentModel",
]