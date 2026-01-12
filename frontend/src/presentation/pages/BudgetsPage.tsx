import React, { useState } from 'react';
import { Plus, Calendar } from 'lucide-react';
import { useBudgets } from '../../application/hooks/useBudgets';
import { BudgetCard } from '../components/BudgetCard';

export const BudgetsPage: React.FC = () => {
  const currentUserId = 1; // TODO: Get from auth context
  const currentDate = new Date();
  const currentPeriod = `${currentDate.getFullYear()}${String(currentDate.getMonth() + 1).padStart(2, '0')}`;
  
  const [selectedPeriod, setSelectedPeriod] = useState(currentPeriod);

  const { data: budgets, isLoading } = useBudgets(selectedPeriod, currentUserId);

  const generatePeriodOptions = () => {
    const options = [];
    const startYear = 2024;
    const endYear = currentDate.getFullYear() + 1;

    for (let year = endYear; year >= startYear; year--) {
      for (let month = 12; month >= 1; month--) {
        const period = `${year}${String(month).padStart(2, '0')}`;
        const date = new Date(year, month - 1);
        const label = date.toLocaleDateString('es-AR', { month: 'long', year: 'numeric' });
        options.push({ value: period, label });
      }
    }

    return options;
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Presupuestos Mensuales</h1>
        <p className="text-gray-600">
          Gestiona y visualiza tus presupuestos compartidos
        </p>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Calendar className="w-5 h-5 text-gray-500" />
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {generatePeriodOptions().map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <button
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          onClick={() => {
            // TODO: Open create budget modal
            alert('Create budget modal - TODO');
          }}
        >
          <Plus className="w-5 h-5" />
          Crear Presupuesto
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Cargando presupuestos...</p>
        </div>
      ) : budgets && budgets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {budgets.map((budget) => (
            <BudgetCard key={budget.id} budget={budget} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">
            No hay presupuestos para este período
          </h3>
          <p className="text-gray-600 mb-4">
            Crea un nuevo presupuesto para comenzar a organizar tus gastos compartidos
          </p>
          <button
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            onClick={() => {
              // TODO: Open create budget modal
              alert('Create budget modal - TODO');
            }}
          >
            <Plus className="w-5 h-5" />
            Crear Primer Presupuesto
          </button>
        </div>
      )}
    </div>
  );
};
