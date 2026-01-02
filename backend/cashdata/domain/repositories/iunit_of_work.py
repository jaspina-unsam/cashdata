from abc import ABC, abstractmethod

from cashdata.domain.repositories import (
    IUserRepository,
    IMonthlyIncomeRepository,
    ICategoryRepository,
    ICreditCardRepository,
    IPurchaseRepository,
    IInstallmentRepository
)

class IUnitOfWork(ABC):
    users: IUserRepository
    monthly_incomes: IMonthlyIncomeRepository
    categories: ICategoryRepository
    credit_cards: ICreditCardRepository
    purchases: IPurchaseRepository
    installments: IInstallmentRepository

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