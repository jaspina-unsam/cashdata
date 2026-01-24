/**
 * Domain Entity: User
 * 
 * Represents a user in the system.
 * Users own credit cards, purchases, and track their finances.
 */
export interface User {
  id: number;
  name: string;
  email: string;
  wage_amount: string;
  wage_currency: string;
}

/**
 * Domain Entity: Monthly Budget
 * 
 * Represents a monthly budget for tracking shared expenses.
 */
export interface MonthlyBudget {
  id: number;
  name: string;
  description?: string;
  status: 'active' | 'closed' | 'archived';
  created_by_user_id: number;
  participant_count: number;
  created_at?: string;
  updated_at?: string;
}

export interface BudgetExpense {
  id: number;
  budget_id: number;
  purchase_id?: number;
  installment_id?: number;
  paid_by_user_id: number;
  paid_by_user_name?: string;
  snapshot_description: string;
  snapshot_amount: number;
  snapshot_currency: string;
  snapshot_date: string;
  split_type: 'equal' | 'proportional' | 'custom' | 'full_single';
}

export interface BudgetExpenseResponsibility {
  id: number;
  budget_expense_id: number;
  user_id: number;
  user_name?: string;
  percentage: number;
  responsible_amount: number;
  currency: string;
}

export interface BudgetBalance {
  user_id: number;
  user_name: string;
  paid: number;
  responsible: number;
  balance: number; // positive = owed, negative = owes
  currency: string;
}

export interface BudgetDebt {
  from_user_id: number;
  from_user_name: string;
  to_user_id: number;
  to_user_name: string;
  amount: number;
  currency: string;
}

export interface BudgetDetails {
  budget: MonthlyBudget;
  expenses: BudgetExpense[];
  responsibilities: Record<number, BudgetExpenseResponsibility[]>; // expense_id -> responsibilities[]
  balances: BudgetBalance[];
  debt_summary: BudgetDebt[];
}

/**
 * Domain Entity: Category
 * 
 * Represents a spending category for purchases.
 */
export interface Category {
  id: number;
  name: string;
  color: string;
  icon?: string;
}

/**
 * Domain Entity: Credit Card
 * 
 * Represents a credit card used for purchases.
 */
export interface CreditCard {
  id: number;
  user_id: number;
  name: string;
  bank: string;
  last_four_digits: string;
  billing_close_day: number;
  payment_due_day: number;
  credit_limit_amount?: string;
  credit_limit_currency?: string;
}

/**
 * Domain Entity: Purchase
 * 
 * Represents a purchase made with a credit card.
 */
export interface Purchase {
  id: number;
  user_id: number;
  payment_method_id: number;
  category_id: number;
  purchase_date: string;
  description: string;
  total_amount: number | string; // number when sending, string when receiving from API
  currency: string;
  installments_count: number;
  // Dual-currency fields
  original_amount?: number | string;
  original_currency?: string;
  exchange_rate_id?: number;
}

/**
 * Domain Entity: Installment
 * 
 * Represents a single installment of a purchase.
 */
export interface Installment {
  id: number;
  purchase_id: number;
  installment_number: number;
  total_installments: number;
  amount: string;
  currency: string;
  billing_period: string;
  due_date: string;
  monthly_statement_id: number;
  manually_assigned_statement_id?: number | null;
  // Dual-currency fields
  original_amount?: string;
  original_currency?: string;
  exchange_rate_id?: number;
}

/**
 * Domain Entity: Credit Card Summary
 * 
 * Represents the summary of installments for a credit card in a billing period.
 */
export interface CreditCardSummary {
  credit_card_id: number;
  billing_period: string;
  total_amount: string;
  total_currency: string;
  installments: Installment[];
}

/**
 * Domain Entity: Monthly Statement
 * 
 * Represents a monthly statement for a credit card.
 * Each statement has explicit period boundaries with start, closing, and due dates.
 */
export interface MonthlyStatement {
  id: number;
  credit_card_id: number;
  credit_card_name: string;
  start_date: string; // ISO date format (YYYY-MM-DD) - period start
  closing_date: string; // ISO date format (YYYY-MM-DD) - billing close
  due_date: string; // ISO date format (YYYY-MM-DD) - payment due
}

/**
 * Domain Entity: Purchase in Statement
 * 
 * Represents a purchase or installment within a statement period.
 */
export interface PurchaseInStatement {
  id: number;
  description: string;
  purchase_date: string; // ISO date format (YYYY-MM-DD)
  amount: number;
  currency: string;
  installments: number;
  installment_number: number | null; // null for full purchases, 1-N for installments
  category_name: string;
  // Dual-currency fields
  original_amount?: number;
  original_currency?: string;
  exchange_rate_id?: number;
}

/**
 * Domain Entity: Statement Detail
 * 
 * Represents the full detail of a monthly statement including all purchases.
 */
export interface StatementDetail {
  id: number;
  credit_card_id: number;
  credit_card_name: string;
  start_date: string; // ISO date format (YYYY-MM-DD), period start
  closing_date: string; // ISO date format (YYYY-MM-DD)
  due_date: string; // ISO date format (YYYY-MM-DD)
  period_start_date: string; // ISO date format (YYYY-MM-DD)
  period_end_date: string; // ISO date format (YYYY-MM-DD)
  purchases: PurchaseInStatement[];
  total_amount: number;
  currency: string;
}

/**
 * Dashboard Metrics & Analytics entities (Fase 1b)
 */
export interface DashboardMetrics {
  totalBalance: number;
  incomeThisMonth: number;
  expensesThisMonth: number;
  netBalance: number;
  incomeTrend: number; // % change vs previous month
  expensesTrend: number; // % change vs previous month
  balanceTrend: number; // % change vs last 6 months average
}

export interface UpcomingInstallmentGroup {
  month: string; // "2026-02"
  paymentMethodId: number;
  paymentMethodName: string; // "Visa *1234"
  totalAmount: number;
  installmentCount: number;
  statementId: number;
}

export interface ExpensesByMonth {
  month: string; // "2026-01"
  amount: number;
}

export interface ExpensesByCategory {
  categoryName: string;
  amount: number;
  percentage: number;
}

export interface IncomesByMonth {
  month: string; // "2026-01"
  amount: number;
}

export interface PaymentMethod {
  id: number;
  user_id: number;
  type: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CashAccount {
  id: number;
  payment_method_id: number;
  user_id: number;
  name: string;
  currency: string;
}

export interface BankAccount {
  id: number;
  payment_method_id: number;
  primary_user_id: number;
  secondary_user_id: number | null;
  name: string;
  bank: string;
  account_type: string;
  last_four_digits: string;
  currency: string;
}

export interface DigitalWallet {
  id: number;
  payment_method_id: number;
  user_id: number;
  name: string;
  provider: string;
  identifier: string;
  currency: string;
}

/**
 * Domain Entity: Monthly Budget
 * 
 * Represents a shared budget for a specific period.
 */
export interface MonthlyBudget {
  id: number;
  name: string;

  description?: string;
  status: 'active' | 'closed' | 'archived';
  created_by_user_id: number;
  participant_count: number;
  created_at?: string;
  updated_at?: string;
}

/**
 * Domain Entity: Budget Expense
 * 
 * Represents an expense assigned to a budget (purchase or installment).
 */
export interface BudgetExpense {
  id: number;
  budget_id: number;
  purchase_id?: number;
  installment_id?: number;
  paid_by_user_id: number;
  paid_by_user_name?: string;
  snapshot_description: string;
  snapshot_amount: number;
  snapshot_currency: string;
  snapshot_date: string;
  split_type: 'equal' | 'proportional' | 'custom' | 'full_single';
}

/**
 * Domain Entity: Budget Expense Responsibility
 * 
 * Represents how much each user is responsible for in an expense.
 */
export interface BudgetExpenseResponsibility {
  id: number;
  budget_expense_id: number;
  user_id: number;
  user_name?: string;
  percentage: number;
  responsible_amount: number;
  currency: string;
}

/**
 * Domain Entity: Budget Balance
 * 
 * Calculated balance for a user in a budget.
 */
export interface BudgetBalance {
  user_id: number;
  user_name: string;
  paid: number;
  responsible: number;
  balance: number; // positive = owed, negative = owes
  currency: string;
}

/**
 * Domain Entity: Budget Debt
 * 
 * Represents a debt between two users in a budget.
 */
export interface BudgetDebt {
  from_user_id: number;
  from_user_name: string;
  to_user_id: number;
  to_user_name: string;
  amount: number;
  currency: string;
}

/**
 * Domain Aggregate: Budget Details
 * 
 * Complete budget information with all related data.
 */
export interface BudgetDetails {
  budget: MonthlyBudget;
  expenses: BudgetExpense[];
  responsibilities: Record<number, BudgetExpenseResponsibility[]>; // expense_id -> responsibilities[]
  balances: BudgetBalance[];
  debt_summary: BudgetDebt[];
}

/**
 * Domain Entity: Financial Projection Configuration
 * 
 * Configuration for generating 5-year financial projections.
 */
export interface ProjectionConfig {
  // User data
  userId: number;
  currentMonthlyIncome: number;      // In USD
  
  // Expenses (calculated or adjustable)
  fixedExpenses: number;             // In USD (e.g., 900)
  variableExpenses: number;          // In USD (e.g., 400)
  emergencyFundContribution: number; // In USD (e.g., 100)
  
  // Professional scenarios
  professionalScenario: 'conservative' | 'moderate' | 'optimistic' | 'very_optimistic';
  annualRaisePercentage: number;     // % (0, 10, 15, 25)
  
  // Economic factors
  constructionInflationRate: number; // % annual (e.g., 8)
  devaluationRate: number;           // % annual (e.g., 0) - future ARS support
  
  // Savings goal
  targetAmount: number;              // In USD (e.g., 75000)
  investmentReturn: number;          // % annual (e.g., 7)
}

/**
 * Domain Entity: Monthly Projection
 * 
 * Represents financial projection for a single month.
 */
export interface MonthlyProjection {
  month: number;                     // 1-60
  date: Date;
  income: number;
  fixedExpenses: number;
  variableExpenses: number;
  monthlySavings: number;
  accumulatedSavings: number;
  accumulatedEmergencyFund: number;
  targetCost: number;                // Cost adjusted by inflation
  difference: number;                // accumulatedSavings - targetCost
  bonus: number;                     // Aguinaldo (month 6, 12, 18, etc.)
}

/**
 * Domain Entity: Projection Summary
 * 
 * Summary of complete 5-year projection.
 */
export interface ProjectionSummary {
  totalSaved: number;
  finalTargetCost: number;
  achievesGoal: boolean;
  surplusOrDeficit: number;
  finalEmergencyFund: number;
  averageMonthlyIncome: number;
  averageMonthlySavings: number;
}

/**
 * Domain Aggregate: Projection Result
 * 
 * Complete projection with monthly data, summary and recommendations.
 */
export interface ProjectionResult {
  months: MonthlyProjection[];
  summary: ProjectionSummary;
  recommendations: string[];
}