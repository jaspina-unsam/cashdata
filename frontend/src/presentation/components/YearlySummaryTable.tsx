/**
 * Component: YearlySummaryTable
 * 
 * Table showing year-by-year breakdown of income, savings, and bonuses.
 */

import React from 'react';
import type { MonthlyProjection } from '@/domain/entities';

interface YearlySummaryTableProps {
  data: MonthlyProjection[];
}

export function YearlySummaryTable({ data }: YearlySummaryTableProps) {
  const years = [2026, 2027, 2028, 2029, 2030];
  
  const yearlyData = years.map(year => {
    const yearData = data.filter(m => m.date.getFullYear() === year);
    const firstMonth = yearData[0];
    const lastMonth = yearData[yearData.length - 1];
    const bonuses = yearData.reduce((sum, m) => sum + m.bonus, 0);
    const saved = lastMonth.accumulatedSavings - (firstMonth.accumulatedSavings || 0);
    
    return {
      year,
      avgIncome: Math.round((firstMonth.income + lastMonth.income) / 2),
      saved: Math.round(saved),
      bonuses: Math.round(bonuses),
      total: Math.round(lastMonth.accumulatedSavings),
    };
  });
  
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };
  
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <h3 className="text-lg font-bold text-slate-800 mb-4">
        📅 Resumen año por año
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-100">
            <tr>
              <th className="p-3 text-left">Año</th>
              <th className="p-3 text-right">Ingreso promedio</th>
              <th className="p-3 text-right">Ahorrado en el año</th>
              <th className="p-3 text-right">Aguinaldos</th>
              <th className="p-3 text-right">Total acumulado</th>
            </tr>
          </thead>
          <tbody>
            {yearlyData.map((year, i) => (
              <tr key={year.year} className={i % 2 === 0 ? 'bg-slate-50' : ''}>
                <td className="p-3 font-bold">{year.year}</td>
                <td className="p-3 text-right">{formatCurrency(year.avgIncome)}</td>
                <td className="p-3 text-right text-green-600 font-semibold">
                  {formatCurrency(year.saved)}
                </td>
                <td className="p-3 text-right text-emerald-600">
                  {formatCurrency(year.bonuses)}
                </td>
                <td className="p-3 text-right font-bold text-blue-600">
                  {formatCurrency(year.total)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
