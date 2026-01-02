# backend/cashdata/infrastructure/persistence/repositories/sqlalchemy_unit_of_work.py
from cashdata.domain.repositories import IUnitOfWork
from cashdata.infrastructure.persistence.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from cashdata.infrastructure.persistence.repositories.sqlalchemy_monthly_income_repository import (
    SQLAlchemyMonthlyIncomeRepository,
)
from cashdata.infrastructure.persistence.repositories.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)
from cashdata.infrastructure.persistence.repositories.sqlalchemy_credit_card_repository import (
    SQLAlchemyCreditCardRepository,
)
from cashdata.infrastructure.persistence.repositories.sqlalchemy_purchase_repository import (
    SQLAlchemyPurchaseRepository,
)
from cashdata.infrastructure.persistence.repositories.sqlalchemy_installment_repository import (
    SQLAlchemyInstallmentRepository,
)
from cashdata.infrastructure.persistence.repositories.sqlalchemy_monthly_statement_repository import (
    SQLAlchemyMonthlyStatementRepository,
)


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None

    def __enter__(self):
        self.session = self.session_factory()
        self.users = SQLAlchemyUserRepository(self.session)
        self.monthly_incomes = SQLAlchemyMonthlyIncomeRepository(self.session)
        self.categories = SQLAlchemyCategoryRepository(self.session)
        self.credit_cards = SQLAlchemyCreditCardRepository(self.session)
        self.purchases = SQLAlchemyPurchaseRepository(self.session)
        self.installments = SQLAlchemyInstallmentRepository(self.session)
        self.monthly_statements = SQLAlchemyMonthlyStatementRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
