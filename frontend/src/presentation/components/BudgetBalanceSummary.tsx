import React from 'react';
import { DollarSign, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { BudgetBalance, BudgetDebt } from '../../domain/entities';

interface BudgetBalanceSummaryProps {
  balances: BudgetBalance[];
  debts: BudgetDebt[];
}

export const BudgetBalanceSummary: React.FC<BudgetBalanceSummaryProps> = ({
  balances,
  debts,
}) => {
  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
      <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <DollarSign className="w-6 h-6 text-blue-600" />
        Resumen de Balances
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {balances.map((balance) => {
          const isOwed = balance.balance > 0;
          const isBalanced = balance.balance === 0;
          const owes = balance.balance < 0;

          return (
            <div
              key={balance.user_id}
              className="bg-white rounded-lg p-4 shadow-sm border border-gray-200"
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900">{balance.user_name}</h3>
                {isBalanced ? (
                  <Minus className="w-5 h-5 text-gray-400" />
                ) : isOwed ? (
                  <TrendingUp className="w-5 h-5 text-green-600" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-red-600" />
                )}
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between text-gray-600">
                  <span>Pagó:</span>
                  <span className="font-medium">
                    ${balance.paid.toFixed(2)} {balance.currency}
                  </span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Debe:</span>
                  <span className="font-medium">
                    ${balance.responsible.toFixed(2)} {balance.currency}
                  </span>
                </div>
                <div
                  className={`flex justify-between font-semibold pt-2 border-t ${
                    isOwed
                      ? 'text-green-700'
                      : owes
                      ? 'text-red-700'
                      : 'text-gray-700'
                  }`}
                >
                  <span>Balance:</span>
                  <span>
                    {isOwed ? '+' : ''}${Math.abs(balance.balance).toFixed(2)}{' '}
                    {balance.currency}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {debts.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-blue-200">
          <h3 className="font-semibold text-gray-900 mb-3">📊 Deudas Pendientes</h3>
          <div className="space-y-2">
            {debts.map((debt, index) => (
              <div
                key={index}
                className="flex items-center justify-between text-sm p-2 bg-gray-50 rounded"
              >
                <span className="text-gray-700">
                  <span className="font-medium">{debt.from_user_name}</span> debe a{' '}
                  <span className="font-medium">{debt.to_user_name}</span>
                </span>
                <span className="font-semibold text-red-700">
                  ${debt.amount.toFixed(2)} {debt.currency}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {debts.length === 0 && balances.length > 0 && (
        <div className="bg-green-50 rounded-lg p-4 border border-green-200 text-center">
          <p className="text-green-800 font-medium">
            ✓ Todas las cuentas están saldadas
          </p>
        </div>
      )}
    </div>
  );
};
