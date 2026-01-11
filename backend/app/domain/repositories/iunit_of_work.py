from abc import ABC, abstractmethod

from app.domain.repositories import (
    IUserRepository,
    IMonthlyIncomeRepository,
    ICategoryRepository,
    ICreditCardRepository,
    IPurchaseRepository,
    IInstallmentRepository,
)
from app.domain.repositories.icash_account_repository import ICashAccountRepository
from app.domain.repositories.imonthly_statement_repository import (
    IMonthlyStatementRepository,
)
from app.domain.repositories.ipayment_method_repository import IPaymentMethodRepository


class IUnitOfWork(ABC):
    users: IUserRepository
    monthly_incomes: IMonthlyIncomeRepository
    categories: ICategoryRepository
    credit_cards: ICreditCardRepository
    purchases: IPurchaseRepository
    installments: IInstallmentRepository
    payment_methods: IPaymentMethodRepository
    monthly_statements: IMonthlyStatementRepository
    cash_accounts: ICashAccountRepository

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
