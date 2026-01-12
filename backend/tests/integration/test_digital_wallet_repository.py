import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.persistence.models.user_model import UserModel
from app.domain.entities.user import User
from app.domain.value_objects.money import Money
from decimal import Decimal
from app.infrastructure.persistence.models.payment_method_model import PaymentMethodModel
from app.infrastructure.persistence.models.digital_wallet_model import DigitalWalletModel
from app.infrastructure.persistence.repositories.sqlalchemy_unit_of_work import (
    SQLAlchemyUnitOfWork,
)
from app.domain.entities.payment_method import PaymentMethod
from app.domain.value_objects.payment_method_type import PaymentMethodType
from app.domain.value_objects.money import Currency


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite:///:memory:")
    UserModel.metadata.create_all(engine)
    PaymentMethodModel.metadata.create_all(engine)
    DigitalWalletModel.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine)
    yield SessionFactory


def test_save_and_find_digital_wallet(session_factory):
    with SQLAlchemyUnitOfWork(session_factory) as uow:
        # create a user properly
        user = User(id=None, name='Test', email='t@t.com', wage=Money(Decimal('1000'), Currency.ARS))
        saved_user = uow.users.save(user)

        pm = uow.payment_methods.save(
            PaymentMethod(id=None, user_id=saved_user.id, type=PaymentMethodType.DIGITAL_WALLET, name="DW1")
        )

        # Create a DigitalWallet entity
        from app.domain.entities.digital_wallet import DigitalWallet as DWEntity

        wallet_entity = DWEntity(
            id=None,
            payment_method_id=pm.id,
            user_id=saved_user.id,
            name='Mercado',
            provider='mercadopago',
            identifier='abc',
            currency=Currency.ARS,
        )

        wallet = uow.digital_wallets.save(wallet_entity)

        assert wallet is not None
        found = uow.digital_wallets.find_by_user_id(1)
        assert len(found) == 1
        assert found[0].provider == 'mercadopago'
