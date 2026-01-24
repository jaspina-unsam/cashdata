import React from 'react';
import { useDashboardMetrics } from '../../../application/hooks/useDashboardData';

interface MetricsSectionProps {
  period?: string;
  onPeriodChange?: (period: string) => void;
}

export const MetricsSection: React.FC<MetricsSectionProps> = ({ period = 'current-month' }) => {
  const { data: metrics, isLoading } = useDashboardMetrics(period);

  if (isLoading) return <div>Cargando métricas...</div>;
  if (!metrics) return <div>No hay datos disponibles.</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Balance Total */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-600">Balance Total</h3>
        <p className={`text-3xl font-bold mt-2 ${metrics.totalBalance > 0 ? 'text-green-600' : 'text-gray-600'}`}>
          ${metrics.totalBalance.toFixed(2)}
        </p>
        <p className="text-sm text-gray-500 mt-1">
          {metrics.balanceTrend > 0 ? '+' : ''}{metrics.balanceTrend.toFixed(1)}% vs 6m
        </p>
      </div>

      {/* Ingresos del Mes */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-600">Ingresos del Mes</h3>
        <p className="text-3xl font-bold mt-2 text-green-600">↑ ${metrics.incomeThisMonth.toFixed(2)}</p>
        <p className="text-sm text-gray-500 mt-1">{metrics.incomeTrend > 0 ? '+' : ''}{metrics.incomeTrend.toFixed(1)}% vs ant.</p>
      </div>

      {/* Gastos del Mes */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-600">Gastos del Mes</h3>
        <p className="text-3xl font-bold mt-2 text-red-600">↓ ${metrics.expensesThisMonth.toFixed(2)}</p>
        <p className="text-sm text-gray-500 mt-1">{metrics.expensesTrend > 0 ? '+' : ''}{metrics.expensesTrend.toFixed(1)}% vs ant.</p>
      </div>

      {/* Balance Neto */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-600">Balance Neto</h3>
        <p className={`text-3xl font-bold mt-2 ${metrics.netBalance > 0 ? 'text-green-600' : 'text-red-600'}`}>
          ${metrics.netBalance.toFixed(2)}
        </p>
        <p className="text-sm text-gray-500 mt-1">{metrics.netBalance > 0 ? 'Superávit' : 'Déficit'}</p>
      </div>
    </div>
  );
};
