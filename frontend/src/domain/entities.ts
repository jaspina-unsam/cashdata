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
  credit_card_id: number;
  category_id: number;
  purchase_date: string;
  description: string;
  total_amount: string;
  total_currency: string;
  installments_count: number;
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
