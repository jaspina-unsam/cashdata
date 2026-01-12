# backend/cashdata/infrastructure/persistence/repositories/sqlalchemy_unit_of_work.py
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.infrastructure.persistence.repositories.sqlalchemy_bank_account_repository import SQLAlchemyBankAccountRepository
from app.infrastructure.persistence.repositories.sqlalchemy_payment_method_repository import SQLAlchemyPaymentMethodRepository
from app.infrastructure.persistence.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.infrastructure.persistence.repositories.sqlalchemy_monthly_income_repository import SQLAlchemyMonthlyIncomeRepository
from app.infrastructure.persistence.repositories.sqlalchemy_monthly_budget_repository import SQLAlchemyMonthlyBudgetRepository
from app.infrastructure.persistence.repositories.sqlalchemy_category_repository import SQLAlchemyCategoryRepository
from app.infrastructure.persistence.repositories.sqlalchemy_credit_card_repository import SQLAlchemyCreditCardRepository
from app.infrastructure.persistence.repositories.sqlalchemy_purchase_repository import SQLAlchemyPurchaseRepository
from app.infrastructure.persistence.repositories.sqlalchemy_installment_repository import SQLAlchemyInstallmentRepository
from app.infrastructure.persistence.repositories.sqlalchemy_monthly_statement_repository import SQLAlchemyMonthlyStatementRepository
from app.infrastructure.persistence.repositories.sqlalchemy_cash_account_repository import SQLAlchemyCashAccountRepository
from app.infrastructure.persistence.repositories.sqlalchemy_budget_expense_repository import SQLAlchemyBudgetExpenseRepository
from app.infrastructure.persistence.repositories.sqlalchemy_budget_expense_responsibility_repository import SQLAlchemyBudgetExpenseResponsibilityRepository
from app.infrastructure.persistence.repositories.sqlalchemy_budget_participant_repository import SQLAlchemyBudgetParticipantRepository
from app.infrastructure.persistence.repositories.sqlalchemy_digital_wallet_repository import SQLAlchemyDigitalWalletRepository


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None

    def __enter__(self):
        self.session = self.session_factory()
        self.users = SQLAlchemyUserRepository(self.session)
        self.monthly_incomes = SQLAlchemyMonthlyIncomeRepository(self.session)
        self.monthly_budgets = SQLAlchemyMonthlyBudgetRepository(self.session)
        self.budget_expenses = SQLAlchemyBudgetExpenseRepository(self.session)
        self.budget_expense_responsibilities = SQLAlchemyBudgetExpenseResponsibilityRepository(self.session)
        self.budget_participants = SQLAlchemyBudgetParticipantRepository(self.session)
        self.categories = SQLAlchemyCategoryRepository(self.session)
        self.credit_cards = SQLAlchemyCreditCardRepository(self.session)
        self.purchases = SQLAlchemyPurchaseRepository(self.session)
        self.installments = SQLAlchemyInstallmentRepository(self.session)
        self.monthly_statements = SQLAlchemyMonthlyStatementRepository(self.session)
        self.payment_methods = SQLAlchemyPaymentMethodRepository(self.session)
        self.cash_accounts = SQLAlchemyCashAccountRepository(self.session)
        self.digital_wallets = SQLAlchemyDigitalWalletRepository(self.session)
        self.bank_accounts = SQLAlchemyBankAccountRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
