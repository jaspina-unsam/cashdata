import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  BarChart,
  Bar,
} from 'recharts';
import { useExpensesByMonth, useExpensesByCategory, useIncomesByMonth } from '../../../application/hooks/useDashboardData';
import { useCurrencyPreference } from '../../../application/contexts/CurrencyContext';

const COLORS = ['#2563EB', '#10B981', '#F97316', '#EF4444', '#8B5CF6', '#F59E0B'];

export const AnalyticsSection: React.FC<{ months?: number; onMonthsChange?: (m: number) => void }> = ({ months = 6, onMonthsChange }) => {
  const { data: expensesByMonth, isLoading: loadingExpMonth } = useExpensesByMonth(months);
  const { data: expensesByCategory, isLoading: loadingExpCat } = useExpensesByCategory(months);
  const { data: incomesByMonth, isLoading: loadingIncomes } = useIncomesByMonth(months);
  const { preference } = useCurrencyPreference();
  const currency = preference.currency;

  const formatCurrency = (value: number) => {
    if (!Number.isFinite(value)) return '-';
    const rounded = Number(value || 0).toFixed(2);
    return currency === 'USD' ? `$${Number(rounded).toLocaleString()}` : `ARS ${Number(rounded).toLocaleString()}`;
  };

  // Prepare data for charts
  const lineData = (expensesByMonth || []).map(d => ({ month: new Date(d.month + '-01').toLocaleString(undefined, { month: 'short', year: 'numeric' }), amount: d.amount }));
  const pieData = (expensesByCategory || []).map(d => ({ name: d.categoryName, value: d.amount }));
  const barData = (incomesByMonth || []).map(d => ({ month: new Date(d.month + '-01').toLocaleString(undefined, { month: 'short', year: 'numeric' }), amount: d.amount }));

  if (loadingExpMonth && loadingExpCat && loadingIncomes) return <div>Cargando analytics...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Analytics</h3>
        <select
          value={months}
          onChange={(e) => onMonthsChange && onMonthsChange(Number(e.target.value))}
          className="border rounded px-2 py-1 text-sm"
        >
          <option value={3}>3 meses</option>
          <option value={6}>6 meses</option>
          <option value={12}>12 meses</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h4 className="text-sm font-medium mb-2">Gastos por mes</h4>
          {(!lineData || lineData.length === 0) ? (
            <div className="text-sm text-gray-500">No hay datos</div>
          ) : (
            <div style={{ height: 220 }}>
              <ResponsiveContainer>
                <LineChart data={lineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value: any) => formatCurrency(Number(value || 0))} />
                  <Line type="monotone" dataKey="amount" stroke="#2563EB" strokeWidth={2} dot />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h4 className="text-sm font-medium mb-2">Gastos por categoría</h4>
          {(!pieData || pieData.length === 0) ? (
            <div className="text-sm text-gray-500">No hay gastos registrados</div>
          ) : (
            <div style={{ height: 220 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={(entry) => `${entry.name}`}>
                    {pieData.map((_, idx) => (
                      <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h4 className="text-sm font-medium mb-2">Ingresos por mes</h4>
          {(!barData || barData.length === 0) ? (
            <div className="text-sm text-gray-500">No hay datos</div>
          ) : (
            <div style={{ height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value: any) => formatCurrency(Number(value || 0))} />
                  <Bar dataKey="amount" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
