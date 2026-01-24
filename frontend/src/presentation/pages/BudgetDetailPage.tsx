import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Plus, Calendar, DollarSign } from 'lucide-react';
import { useBudgetDetails, useRemoveExpense } from '../../application/hooks/useBudgets';
import { BudgetBalanceSummary } from '../components/BudgetBalanceSummary';
import { AddExpenseToBudgetModal } from '../components/AddExpenseToBudgetModal';
import { EditExpenseModal } from '../components/EditExpenseModal';
import { DeleteExpenseConfirmation } from '../components/DeleteExpenseConfirmation';
import { useActiveUser } from '../../application/contexts/UserContext';

export const BudgetDetailPage: React.FC = () => {
  const { budgetId } = useParams<{ budgetId: string }>();
  const { activeUserId } = useActiveUser();

  const [isAddExpenseModalOpen, setIsAddExpenseModalOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState<{ id: number; splitType: string; description: string } | null>(null);
  const [deletingExpense, setDeletingExpense] = useState<{ id: number; description: string } | null>(null);

  const { data: budgetDetails, isLoading, error } = useBudgetDetails(
    budgetId ? parseInt(budgetId) : undefined,
    activeUserId
  );
  
  const removeExpenseMutation = useRemoveExpense();

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Cargando detalles del presupuesto...</p>
        </div>
      </div>
    );
  }

  if (error) {
    console.error('Error loading budget details:', error);
  }

  if (!budgetDetails) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <p className="text-gray-600">Presupuesto no encontrado</p>
          {error && <p className="text-red-600 text-sm mt-2">Error: {String(error)}</p>}
          <Link to="/budgets" className="text-blue-600 hover:underline mt-2 inline-block">
            Volver a presupuestos
          </Link>
        </div>
      </div>
    );
  }

  const { budget, expenses = [], responsibilities = [], balances = [], debt_summary = [] } = budgetDetails;

  if (!budget) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <p className="text-gray-600">Presupuesto no encontrado</p>
          <Link to="/budgets" className="text-blue-600 hover:underline mt-2 inline-block">
            Volver a presupuestos
          </Link>
        </div>
      </div>
    );
  }
  const participants = balances.map(b => ({ id: b.user_id, name: b.user_name }));

  const handleDeleteExpense = async () => {
    if (!deletingExpense || !budgetId) return;

    try {
      await removeExpenseMutation.mutateAsync({
        budgetId: parseInt(budgetId),
        expenseId: deletingExpense.id,
        userId: activeUserId,
      });
      setDeletingExpense(null);
    } catch (error) {
      console.error('Error deleting expense:', error);
      alert('Error al eliminar el gasto');
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit' });
  };

  const getSplitTypeLabel = (splitType: string) => {
    switch (splitType) {
      case 'equal':
        return '50/50 (Partes iguales)';
      case 'proportional':
        return 'Proporcional (según ingresos)';
      case 'custom':
        return 'Personalizado';
      case 'full_single':
        return '100% una persona';
      default:
        return splitType;
    }
  };

  const totalAmount = expenses.reduce((sum, exp) => sum + (Number(exp.snapshot_amount) || 0), 0);

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/budgets"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Volver a presupuestos
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{budget.name}</h1>
            {budget.created_at && (
              <p className="text-gray-600 mt-1">
                Creado el {new Date(budget.created_at).toLocaleDateString('es-AR', { 
                  day: 'numeric', 
                  month: 'long', 
                  year: 'numeric' 
                })}
              </p>
            )}
            {budget.description && (
              <p className="text-gray-600 text-sm mt-2">{budget.description}</p>
            )}
          </div>

          <button
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            onClick={() => setIsAddExpenseModalOpen(true)}
          >
            <Plus className="w-5 h-5" />
            Agregar Gasto
          </button>
        </div>
      </div>

      {/* Balance Summary */}
      {balances.length > 0 && (
        <div className="mb-8">
          <BudgetBalanceSummary balances={balances} debts={debt_summary} />
        </div>
      )}

      {/* Expenses List */}
      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Gastos del Presupuesto</h2>
          <button
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            onClick={() => setIsAddExpenseModalOpen(true)}
          >
            <Plus className="w-4 h-4" />
            Agregar
          </button>
        </div>

        {expenses.length === 0 ? (
          <div className="p-8 text-center text-gray-600">
            <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p>No hay gastos registrados en este presupuesto</p>
            <p className="text-sm mt-1">Agrega tu primer gasto para comenzar</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {expenses.map((expense) => {
              const expenseResponsibilities = responsibilities[expense.id] || [];

              return (
                <div key={expense.id} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <span className="text-sm text-gray-500">
                          {formatDate(expense.snapshot_date)}
                        </span>
                        <span className="font-medium text-gray-900">
                          {expense.snapshot_description}
                        </span>
                        <span className="text-sm text-gray-600">
                          Pagó: {expense.paid_by_user_name || `User ${expense.paid_by_user_id}`}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        División: {getSplitTypeLabel(expense.split_type)}
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="font-semibold text-lg text-gray-900">
                        ${(Number(expense.snapshot_amount) || 0).toFixed(2)}
                      </div>
                      <div className="text-sm text-gray-500">{expense.snapshot_currency}</div>
                    </div>
                  </div>

                  {/* Responsibilities breakdown */}
                  {expenseResponsibilities.length > 0 && (
                    <div className="mt-3 pl-4 border-l-2 border-gray-200 space-y-1">
                      {expenseResponsibilities.map((resp) => (
                        <div
                          key={resp.id}
                          className="flex items-center justify-between text-sm"
                        >
                          <span className="text-gray-700">
                            {resp.user_name || `User ${resp.user_id}`}: {resp.percentage}%
                          </span>
                          <span className="text-gray-900 font-medium">
                            ${(Number(resp.responsible_amount) || 0).toFixed(2)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="mt-3 flex gap-2">
                    <button
                      className="text-sm text-blue-600 hover:text-blue-800"
                      onClick={() => {
                        setEditingExpense({
                          id: expense.id,
                          splitType: expense.split_type,
                          description: expense.snapshot_description,
                        });
                      }}
                    >
                      Editar División
                    </button>
                    <button
                      className="text-sm text-red-600 hover:text-red-800"
                      onClick={() => {
                        setDeletingExpense({
                          id: expense.id,
                          description: expense.snapshot_description,
                        });
                      }}
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Total */}
        {expenses.length > 0 && (
          <div className="p-4 bg-gray-50 border-t border-gray-200">
            <div className="flex items-center justify-between font-semibold text-lg">
              <span className="text-gray-900">TOTAL</span>
              <div className="flex items-center gap-2 text-gray-900">
                <DollarSign className="w-5 h-5" />
                <span>${totalAmount.toFixed(2)} ARS</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      <AddExpenseToBudgetModal
        isOpen={isAddExpenseModalOpen}
        onClose={() => setIsAddExpenseModalOpen(false)}
        budgetId={parseInt(budgetId!)}
        currentUserId={activeUserId}
        participants={participants}
      />

      {editingExpense && (
        <EditExpenseModal
          isOpen={true}
          onClose={() => setEditingExpense(null)}
          budgetId={parseInt(budgetId!)}
          expenseId={editingExpense.id}
          currentUserId={activeUserId}
          currentSplitType={editingExpense.splitType as any}
          participants={participants}
          expenseDescription={editingExpense.description}
        />
      )}

      {deletingExpense && (
        <DeleteExpenseConfirmation
          isOpen={true}
          onClose={() => setDeletingExpense(null)}
          onConfirm={handleDeleteExpense}
          expenseDescription={deletingExpense.description}
          isDeleting={removeExpenseMutation.isPending}
        />
      )}
    </div>
  );
};
