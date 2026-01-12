import React from 'react';
import { Link } from 'react-router-dom';
import { Users, Calendar, DollarSign } from 'lucide-react';
import type { MonthlyBudget } from '../../domain/entities';

interface BudgetCardProps {
  budget: MonthlyBudget;
  totalAmount?: number;
}

export const BudgetCard: React.FC<BudgetCardProps> = ({ budget, totalAmount }) => {
  const formatPeriod = (period: string) => {
    const year = period.substring(0, 4);
    const month = period.substring(4, 6);
    const date = new Date(parseInt(year), parseInt(month) - 1);
    return date.toLocaleDateString('es-AR', { month: 'long', year: 'numeric' });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'closed':
        return 'bg-gray-100 text-gray-800';
      case 'archived':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active':
        return 'Activo';
      case 'closed':
        return 'Cerrado';
      case 'archived':
        return 'Archivado';
      default:
        return status;
    }
  };

  return (
    <Link
      to={`/budgets/${budget.id}`}
      className="block p-6 bg-white rounded-lg shadow hover:shadow-md transition-shadow border border-gray-200"
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{budget.name}</h3>
        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(budget.status)}`}>
          {getStatusLabel(budget.status)}
        </span>
      </div>

      {budget.description && (
        <p className="text-sm text-gray-600 mb-4">{budget.description}</p>
      )}

      <div className="flex items-center gap-4 text-sm text-gray-600">
        <div className="flex items-center gap-1">
          <Calendar className="w-4 h-4" />
          <span>{formatPeriod(budget.period)}</span>
        </div>

        <div className="flex items-center gap-1">
          <Users className="w-4 h-4" />
          <span>{budget.participant_count} participante{budget.participant_count !== 1 ? 's' : ''}</span>
        </div>

        {totalAmount !== undefined && (
          <div className="flex items-center gap-1 ml-auto font-medium text-gray-900">
            <DollarSign className="w-4 h-4" />
            <span>${totalAmount.toFixed(2)}</span>
          </div>
        )}
      </div>
    </Link>
  );
};
