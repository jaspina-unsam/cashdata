/**
 * Domain Repository Interfaces
 *
 * Define contracts for data access without implementation details.
 * These interfaces ensure the domain layer is independent of infrastructure.
 */

import type {
  Category,
  CreditCard,
  Purchase,
  Installment,
  CreditCardSummary,
  MonthlyStatement,
  StatementDetail,
  PaymentMethod,
  CashAccount,
  BankAccount,
  DigitalWallet
} from './entities';

/**
 * Repository interface for Category operations
 */
export interface ICategoryRepository {
  findAll(): Promise<Category[]>;
  findById(id: number): Promise<Category | null>;
  create(data: Omit<Category, 'id'>): Promise<Category>;
}

/**
 * Repository interface for Credit Card operations
 */
export interface ICreditCardRepository {
  findByUserId(userId: number, skip?: number, limit?: number): Promise<CreditCard[]>;
  findById(id: number, userId: number): Promise<CreditCard | null>;
  getSummary(id: number, userId: number, billingPeriod: string): Promise<CreditCardSummary>;
  create(userId: number, data: Omit<CreditCard, 'id' | 'user_id'>): Promise<CreditCard>;
  delete(id: number, userId: number): Promise<void>;
}

/**
 * Repository interface for Purchase operations
 */
export interface IPurchaseRepository {
  findByUserId(
    userId: number,
    filters?: { startDate?: string; endDate?: string; skip?: number; limit?: number }
  ): Promise<Purchase[]>;
  findById(id: number, userId: number): Promise<Purchase | null>;
  findByCreditCardId(cardId: number, userId: number, skip?: number, limit?: number): Promise<Purchase[]>;
  findByCategoryId(categoryId: number, userId: number, skip?: number, limit?: number): Promise<Purchase[]>;
  getInstallments(purchaseId: number, userId: number): Promise<Installment[]>;
  create(
    userId: number,
    data: Omit<Purchase, 'id' | 'user_id'>
  ): Promise<Purchase>;
  delete(id: number, userId: number): Promise<void>;
}

/**
 * Repository interface for Monthly Statement operations
 */
export interface IMonthlyStatementRepository {
  findByUserId(userId: number, includeFuture?: boolean): Promise<MonthlyStatement[]>;
  findById(statementId: number, userId: number): Promise<StatementDetail | null>;
  create(userId: number, data: {
    credit_card_id: number;
    closing_date: string;
    due_date: string;
  }): Promise<MonthlyStatement>;
  updateDates(statementId: number, userId: number, data: {
    closing_date: string;
    due_date: string;
  }): Promise<MonthlyStatement>;
}


export interface IPaymentMethodRepository {
  findByUserId(userId: number): Promise<PaymentMethod[]>;
  findById(id: number, userId: number): Promise<PaymentMethod | null>;
}


export interface ICashAccountRepository {
  findByUserId(userId: number): Promise<CashAccount[]>;
  create(
    userId: number,
    data: Omit<CashAccount, "id" | "payment_method_id" | "user_id">
  ): Promise<CashAccount>;
  delete(id: number, userId: number): Promise<void>;
}


export interface IBankAccountRepository {
  findByUserId(userId: number): Promise<BankAccount[]>;
  create(
    userId: number,
    data: Omit<BankAccount, "id" | "payment_method_id">
  ): Promise<BankAccount>;
  delete(id: number, userId: number): Promise<void>;
}


export interface IDigitalWalletRepository {
  findByUserId(userId: number): Promise<DigitalWallet[]>;
  create(
    userId: number,
    data: Omit<DigitalWallet, "id" | "payment_method_id" | "user_id">
  ): Promise<DigitalWallet>;
  delete(id: number, userId: number): Promise<void>;
}