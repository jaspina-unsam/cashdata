from cashdata.domain.entities.user import User
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.infrastructure.persistence.models.user_model import UserModel
from decimal import Decimal


class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        """SQLAlchemy Model → Domain Entity"""
        return User(
            id=model.id,
            name=model.name,
            email=model.email,
            wage=Money(Decimal(str(model.wage_amount)), Currency(model.wage_currency)),
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        """Domain Entity → SQLAlchemy Model"""
        return UserModel(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            wage_amount=float(entity.wage.amount),  # ← Decimal to float
            wage_currency=entity.wage.currency.value,
        )
