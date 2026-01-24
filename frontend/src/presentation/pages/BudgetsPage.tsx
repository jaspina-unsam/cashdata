import React, { useState } from 'react';
import { Plus, Calendar } from 'lucide-react';
import { useBudgets } from '../../application/hooks/useBudgets';
import { BudgetCard } from '../components/BudgetCard';
import { CreateBudgetModal } from '../components/CreateBudgetModal';
import { useActiveUser } from '../../application/contexts/UserContext';

export const BudgetsPage: React.FC = () => {
  const { activeUserId } = useActiveUser();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const { data: budgets, isLoading } = useBudgets(activeUserId);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Presupuestos</h1>
        <p className="text-gray-600">
          Gestiona y visualiza tus presupuestos compartidos
        </p>
      </div>

      <div className="flex items-center justify-end mb-6">
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Crear Presupuesto
        </button>
      </div>

      <CreateBudgetModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        currentUserId={activeUserId}
      />

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
            No hay presupuestos creados
          </h3>
          <p className="text-gray-600 mb-4">
            Crea tu primer presupuesto para comenzar a gestionar tus gastos compartidos
            Crea un nuevo presupuesto para comenzar.
          </p>
          <button
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            onClick={() => setIsCreateModalOpen(true)}
          >
            <Plus className="w-5 h-5" />
            Crear Primer Presupuesto
          </button>
        </div>
      )}
    </div>
  );
};
