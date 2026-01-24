import React from 'react';
import { useUpcomingInstallments } from '../../../application/hooks/useDashboardData';
import { Link } from 'react-router-dom';
import { useCurrencyPreference } from '../../../application/contexts/CurrencyContext';

interface Props {
  months?: number;
  onMonthsChange?: (m: number) => void;
}

export const UpcomingInstallmentsSection: React.FC<Props> = ({ months = 6, onMonthsChange }) => {
  const { data: groups, isLoading } = useUpcomingInstallments(months);
  const { preference } = useCurrencyPreference();
  const currency = preference.currency;

  if (isLoading) return <div>Cargando próximas cuotas...</div>;

  if (!groups || groups.length === 0) return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium">Próximas Cuotas</h3>
      <p className="mt-2 text-gray-600">No hay cuotas pendientes.</p>
    </div>
  );

  // Build months list in order
  const monthsList = Array.from(new Set(groups.map(g => g.month))).slice(0, months);
  // Build payment methods list
  const pmMap = new Map<number, string>();
  groups.forEach(g => pmMap.set(g.paymentMethodId, g.paymentMethodName));
  const paymentMethods = Array.from(pmMap.entries());

  // Totals per month
  const totals = monthsList.map(m => {
    const monthGroups = groups.filter(g => g.month === m);
    const totalAmt = monthGroups.reduce((s, x) => s + x.totalAmount, 0);
    const totalCount = monthGroups.reduce((s, x) => s + x.installmentCount, 0);
    return { totalAmt, totalCount };
  });

  const formatCurrency = (amount: number) => {
    const rounded = Number(amount || 0).toFixed(2);
    return currency === 'USD' ? `$${Number(rounded).toLocaleString()}` : `ARS ${Number(rounded).toLocaleString()}`;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow overflow-auto">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Próximas Cuotas</h3>
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

      <div className="mt-4">
        <table className="min-w-full table-auto">
          <thead>
            <tr>
              <th className="text-left px-3 py-2">Tarjeta / Mes</th>
              {monthsList.map(m => (
                <th key={m} className="text-left px-3 py-2">{new Date(m + '-01').toLocaleString(undefined, { month: 'short', year: 'numeric' })}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paymentMethods.map(([pmId, pmName]) => (
              <tr key={pmId} className="border-t">
                <td className="px-3 py-2 font-medium">{pmName}</td>
                {monthsList.map(m => {
                  const g = groups.find(x => x.month === m && x.paymentMethodId === pmId);
                  return (
                    <td key={m} className="px-3 py-2 text-right align-top">
                      {g ? (
                        <div className="flex flex-col items-end">
                          <div className="font-semibold">{formatCurrency(g.totalAmount)}</div>
                          <div className="text-xs text-gray-500">{g.installmentCount} cuotas</div>
                          <Link to={`/statements/${g.statementId}`} className="mt-2 text-xs text-blue-600 underline">Ver resumen</Link>
                        </div>
                      ) : (
                        <div className="text-sm text-gray-400">-</div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="border-t font-semibold">
              <td className="px-3 py-2">Total por mes</td>
              {totals.map((t, idx) => (
                <td key={idx} className="px-3 py-2 text-right">
                  <div>{formatCurrency(t.totalAmt)}</div>
                  <div className="text-xs text-gray-500">{t.totalCount} cuotas</div>
                </td>
              ))}
            </tr>
          </tfoot>
        </table>

        <div className="mt-4 text-sm text-gray-500">Haz click en "Ver resumen" en la celda correspondiente para ver el statement.</div>
      </div>
    </div>
  );
};
