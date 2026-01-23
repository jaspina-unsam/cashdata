from abc import ABC, abstractmethod

from app.domain.repositories.icash_account_repository import ICashAccountRepository
from app.domain.repositories.icategory_repository import ICategoryRepository
from app.domain.repositories.icredit_card_repository import ICreditCardRepository
from app.domain.repositories.iinstallment_repository import IInstallmentRepository
from app.domain.repositories.imonthly_budget_repository import IMonthlyBudgetRepository
from app.domain.repositories.imonthly_income_repository import IMonthlyIncomeRepository
from app.domain.repositories.imonthly_statement_repository import IMonthlyStatementRepository
from app.domain.repositories.ipayment_method_repository import IPaymentMethodRepository
from app.domain.repositories.ipurchase_repository import IPurchaseRepository
from app.domain.repositories.iuser_repository import IUserRepository
from app.domain.repositories.ibank_account_repository import IBankAccountRepository
from app.domain.repositories.idigital_wallet_repository import IDigitalWalletRepository
from app.domain.repositories.ibudget_expense_repository import IBudgetExpenseRepository
from app.domain.repositories.ibudget_expense_responsibility_repository import IBudgetExpenseResponsibilityRepository
from app.domain.repositories.ibudget_participant_repository import IBudgetParticipantRepository
from app.domain.repositories.iexchange_rate_repository import IExchangeRateRepository


class IUnitOfWork(ABC):
    users: IUserRepository
    monthly_incomes: IMonthlyIncomeRepository
    monthly_budgets: IMonthlyBudgetRepository
    budget_expenses: IBudgetExpenseRepository
    budget_expense_responsibilities: IBudgetExpenseResponsibilityRepository
    budget_participants: IBudgetParticipantRepository
    categories: ICategoryRepository
    credit_cards: ICreditCardRepository
    purchases: IPurchaseRepository
    installments: IInstallmentRepository
    payment_methods: IPaymentMethodRepository
    monthly_statements: IMonthlyStatementRepository
    cash_accounts: ICashAccountRepository
    bank_accounts: IBankAccountRepository
    digital_wallets: IDigitalWalletRepository
    exchange_rates: IExchangeRateRepository

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass
