import { purchaseRepository } from '../api/purchaseRepository';
import { exchangeRateRepository } from '../api/exchangeRatesApi';
import { userRepository } from '../api/userRepository';
import { monthlyStatementRepository } from '../api/monthlyStatementRepository';
import { budgetsRepository } from '../api/budgetsRepository';

import type {
  DashboardMetrics,
  User,
  MonthlyBudget,
  UpcomingInstallmentGroup,
  ExpensesByMonth,
  ExpensesByCategory,
  IncomesByMonth,
} from '../../domain/entities';

function getLastNMonths(n: number): string[] {
  const months: string[] = [];
  const now = new Date();
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    months.push(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
  }
  return months;
}

/**
 * Simplified DashboardRepository for MVP.
 * Orquesta llamadas existentes para calcular métricas en frontend.
 */
export class DashboardRepository {
  private toNumber(value: any): number {
    if (typeof value === 'number') return value;
    const n = Number(value);
    return Number.isFinite(n) ? n : 0;
  }

  private isSameMonth(dateStr: string, monthStr: string) {
    const d = new Date(dateStr);
    const mm = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    return mm === monthStr;
  }

  private getCurrentMonth(): string {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  }

  private getPreviousMonth(): string {
    const now = new Date();
    const prev = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    return `${prev.getFullYear()}-${String(prev.getMonth() + 1).padStart(2, '0')}`;
  }

  private calculateTrend(current: number, previous: number): number {
    if (previous === 0) return current > 0 ? 100 : 0;
    return ((current - previous) / previous) * 100;
  }

  /**
   * Get metrics for a user. Currency is respected in returned values
   * (currency: 'USD' | 'ARS'). For conversion we fetch latest official rate.
   */
  async getMetrics(userId: number, currency: 'USD' | 'ARS' = 'USD', _period: string = 'current-month'): Promise<DashboardMetrics> {
    // Fetch user + purchases + latest official exchange rate in parallel
    const [user, purchasesResp, exchangeRate] = await Promise.all([
      userRepository.findById(userId),
      purchaseRepository.findByUserId(userId, { page: 1, page_size: 1000 }),
      exchangeRateRepository.getLatest(userId, 'official', 'USD', 'ARS').catch(() => null),
    ]);

    const purchases = purchasesResp.items || [];

    const currentMonth = this.getCurrentMonth();
    const previousMonth = this.getPreviousMonth();

    const convertToCurrency = (amount: number, fromCurrency: string) => {
      if (currency === fromCurrency) return amount;
      // Only support USD <-> ARS via official rate for MVP
      if (!exchangeRate) return amount; // no conversion available
      if (fromCurrency === 'ARS' && currency === 'USD') return amount / exchangeRate.rate;
      if (fromCurrency === 'USD' && currency === 'ARS') return amount * exchangeRate.rate;
      return amount;
    };

    // Expenses this month
    const currentMonthPurchases = purchases.filter(p => this.isSameMonth(p.purchase_date, currentMonth));
    const expensesThisMonth = currentMonthPurchases.reduce((sum, p) => {
      const amt = this.toNumber(p.total_amount);
      return sum + convertToCurrency(amt, p.currency);
    }, 0);

    // Expenses previous month
    const previousMonthPurchases = purchases.filter(p => this.isSameMonth(p.purchase_date, previousMonth));
    const expensesPreviousMonth = previousMonthPurchases.reduce((sum, p) => {
      const amt = this.toNumber(p.total_amount);
      return sum + convertToCurrency(amt, p.currency);
    }, 0);

    // Income this month: prefer user's wage if present
    let incomeThisMonth = 0;
    if (user && (user as User).wage_amount) {
      const wage = this.toNumber((user as User).wage_amount);
      const wageCurrency = (user as User).wage_currency || 'USD';
      incomeThisMonth = convertToCurrency(wage, wageCurrency);
    }

    // Income previous month - assume stable wage for MVP
    const incomePreviousMonth = incomeThisMonth;

    const incomeTrend = this.calculateTrend(incomeThisMonth, incomePreviousMonth);
    const expensesTrend = this.calculateTrend(expensesThisMonth, expensesPreviousMonth);

    const netBalance = incomeThisMonth - expensesThisMonth;

    // totalBalance: for MVP we approximate as net of last 6 months (simple sum)
    const last6months = (new Array(6)).fill(0).map((_, idx) => {
      const monthsBack = idx;
      const date = new Date();
      const d = new Date(date.getFullYear(), date.getMonth() - monthsBack, 1);
      const m = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
      const monthPurchases = purchases.filter(p => this.isSameMonth(p.purchase_date, m));
      const monthExpenses = monthPurchases.reduce((s, p) => s + convertToCurrency(this.toNumber(p.total_amount), p.currency), 0);
      const monthIncome = incomeThisMonth; // simplification
      return monthIncome - monthExpenses;
    });

    const avgLast6 = last6months.reduce((s, v) => s + v, 0) / 6;

    const balanceTrend = this.calculateTrend(netBalance, avgLast6 || 0);

    const metrics: DashboardMetrics = {
      totalBalance: avgLast6, // approximation
      incomeThisMonth,
      expensesThisMonth,
      netBalance,
      incomeTrend,
      expensesTrend,
      balanceTrend,
    };

    return metrics;
  }

  async getLatestBudget(userId: number): Promise<MonthlyBudget | null> {
    const budgets = await budgetsRepository.list(userId);
    if (!budgets || budgets.length === 0) return null;
    // sort by created_at desc if available
    budgets.sort((a, b) => {
      const ta = a.created_at ? new Date(a.created_at).getTime() : 0;
      const tb = b.created_at ? new Date(b.created_at).getTime() : 0;
      return tb - ta;
    });
    return budgets[0];
  }

  async getUpcomingInstallments(userId: number, months: number, currency: 'USD' | 'ARS' = 'USD'): Promise<UpcomingInstallmentGroup[]> {
    // Use monthly statements (including future) and fetch statement details to compute totals
    const statements = await monthlyStatementRepository.findByUserId(userId, true);

    // Get latest official rate for conversions
    const exchangeRate = await exchangeRateRepository.getLatest(userId, 'official', 'USD', 'ARS').catch(() => null);

    const convert = (amount: number, fromCurrency: string) => {
      if (fromCurrency === currency) return amount;
      if (!exchangeRate) return amount; // no conversion available
      if (fromCurrency === 'ARS' && currency === 'USD') return amount / exchangeRate.rate;
      if (fromCurrency === 'USD' && currency === 'ARS') return amount * exchangeRate.rate;
      return amount;
    };

    // Sort statements by closing_date ascending to pick upcoming months
    const sorted = statements.sort((a, b) => new Date(a.closing_date).getTime() - new Date(b.closing_date).getTime());

    const selected = sorted.slice(0, months);

    const groups: UpcomingInstallmentGroup[] = [];

    for (const stmt of selected) {
      // Fetch statement detail to get purchases amounts
      const detail = await monthlyStatementRepository.findById(stmt.id, userId);
      const monthKey = `${new Date(stmt.closing_date).getFullYear()}-${String(new Date(stmt.closing_date).getMonth() + 1).padStart(2, '0')}`;

      let totalAmount = 0;
      let installmentCount = 0;

      if (detail && detail.purchases && detail.purchases.length > 0) {
        for (const p of detail.purchases) {
          // p.amount is already a numeric total for the purchase/entry
          const amt = Number(p.amount || 0);
          // assume p.currency equals detail.currency when available
          totalAmount += convert(amt, detail.currency || 'USD');
          installmentCount += 1;
        }
      }

      groups.push({
        month: monthKey,
        paymentMethodId: stmt.credit_card_id,
        paymentMethodName: stmt.credit_card_name,
        totalAmount,
        installmentCount,
        statementId: stmt.id,
      });
    }

    return groups;
  }

  async getExpensesByMonth(userId: number, currency: 'USD' | 'ARS' = 'USD', months: number = 6): Promise<ExpensesByMonth[]> {
    const purchasesResp = await purchaseRepository.findByUserId(userId, { page: 1, page_size: 1000 });
    const purchases = purchasesResp.items || [];
    const exchangeRate = await exchangeRateRepository.getLatest(userId, 'official', 'USD', 'ARS').catch(() => null);

    const convert = (amount: number, fromCurrency: string) => {
      if (fromCurrency === currency) return amount;
      if (!exchangeRate) return amount;
      if (fromCurrency === 'ARS' && currency === 'USD') return amount / exchangeRate.rate;
      if (fromCurrency === 'USD' && currency === 'ARS') return amount * exchangeRate.rate;
      return amount;
    };

    const lastMonths = getLastNMonths(months);

    const grouped = lastMonths.map(month => {
      const monthPurchases = purchases.filter(p => this.isSameMonth(p.purchase_date, month));
      const amount = monthPurchases.reduce((s, p) => s + convert(Number(p.total_amount || 0), p.currency || 'USD'), 0);
      return { month, amount } as ExpensesByMonth;
    });

    return grouped;
  }

  async getExpensesByCategory(userId: number, currency: 'USD' | 'ARS' = 'USD', months: number = 6): Promise<ExpensesByCategory[]> {
    const purchasesResp = await purchaseRepository.findByUserId(userId, { page: 1, page_size: 1000 });
    const purchases = purchasesResp.items || [];
    const exchangeRate = await exchangeRateRepository.getLatest(userId, 'official', 'USD', 'ARS').catch(() => null);

    const convert = (amount: number, fromCurrency: string) => {
      if (fromCurrency === currency) return amount;
      if (!exchangeRate) return amount;
      if (fromCurrency === 'ARS' && currency === 'USD') return amount / exchangeRate.rate;
      if (fromCurrency === 'USD' && currency === 'ARS') return amount * exchangeRate.rate;
      return amount;
    };

    const lastMonths = getLastNMonths(months);
    const filtered = purchases.filter(p => lastMonths.some(m => this.isSameMonth(p.purchase_date, m)));

    const map = new Map<string, number>();
    filtered.forEach(p => {
      const categoryName = (p as any).category?.name || (p as any).category_name || 'Sin categoría';
      const amt = convert(Number(p.total_amount || 0), (p as any).currency || 'USD');
      map.set(categoryName, (map.get(categoryName) || 0) + amt);
    });

    const entries = Array.from(map.entries()).map(([categoryName, amount]) => ({ categoryName, amount }));
    const total = entries.reduce((s, e) => s + e.amount, 0);

    let result: ExpensesByCategory[] = entries.map(e => ({
      categoryName: e.categoryName,
      amount: e.amount,
      percentage: total === 0 ? 0 : (e.amount / total) * 100,
    }));

    result.sort((a, b) => b.amount - a.amount);

    if (result.length > 5) {
      const top5 = result.slice(0, 5);
      const othersTotal = result.slice(5).reduce((s, r) => s + r.amount, 0);
      const othersPercentage = total === 0 ? 0 : (othersTotal / total) * 100;
      result = [...top5, { categoryName: 'Otros', amount: othersTotal, percentage: othersPercentage }];
    }

    return result;
  }

  async getIncomesByMonth(userId: number, currency: 'USD' | 'ARS' = 'USD', months: number = 6): Promise<IncomesByMonth[]> {
    const user = await userRepository.findById(userId);
    const exchangeRate = await exchangeRateRepository.getLatest(userId, 'official', 'USD', 'ARS').catch(() => null);

    const convert = (amount: number, fromCurrency: string) => {
      if (fromCurrency === currency) return amount;
      if (!exchangeRate) return amount;
      if (fromCurrency === 'ARS' && currency === 'USD') return amount / exchangeRate.rate;
      if (fromCurrency === 'USD' && currency === 'ARS') return amount * exchangeRate.rate;
      return amount;
    };

    const wage = user && user.wage_amount ? Number(user.wage_amount) : 0;
    const wageCurrency = user && user.wage_currency ? user.wage_currency : 'USD';

    const lastMonths = getLastNMonths(months);
    return lastMonths.map(m => ({ month: m, amount: convert(wage, wageCurrency) }));
  }
}

export const dashboardRepository = new DashboardRepository();
