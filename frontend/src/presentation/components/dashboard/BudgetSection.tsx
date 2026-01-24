import React from 'react';
import { useLatestBudget } from '../../../application/hooks/useDashboardData';
import { Link } from 'react-router-dom';

export const BudgetSection: React.FC = () => {
  const { data: latestBudget, isLoading } = useLatestBudget();

  if (isLoading) return <div>Cargando presupuesto...</div>;

  if (!latestBudget) return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium">Último Presupuesto</h3>
      <p className="mt-2 text-gray-600">No hay presupuestos creados.</p>
      <div className="mt-4">
        <Link to="/budgets" className="text-sm text-blue-600 font-medium">Crear presupuesto</Link>
      </div>
    </div>
  );

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium">Último Presupuesto</h3>
      <p className="mt-2 text-gray-800 font-semibold">{latestBudget.name}</p>
      <p className="text-sm text-gray-500 mt-1">Participantes: {latestBudget.participant_count}</p>
      <div className="mt-4 flex items-center justify-between">
        <Link to={`/budgets/${latestBudget.id}`} className="text-sm text-blue-600 font-medium">Ver detalles</Link>
        <span className="text-xs text-gray-400">Creado: {latestBudget.created_at ? new Date(latestBudget.created_at).toLocaleDateString() : '—'}</span>
      </div>
    </div>
  );
};
