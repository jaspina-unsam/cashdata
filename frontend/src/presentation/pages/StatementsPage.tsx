/**
 * Statements Page
 * 
 * Displays a list of monthly statements for a user's credit cards.
 * Statements are ordered by payment due date (descending - present to past).
 * Users can toggle to show/hide future statements.
 */

import { useState } from 'react';
import { Link } from 'react-router';
import { useStatements } from '../../application/hooks/useStatements';
import { useActiveUser } from '../../application/contexts/UserContext';

export function StatementsPage() {
  const { activeUserId } = useActiveUser();
  const [includeFuture, setIncludeFuture] = useState(false);

  const { data: statements, isLoading, error } = useStatements(activeUserId, includeFuture);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-gray-600">Cargando resumenes...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-red-600">
          Error al cargar resumenes: {(error as Error).message}
        </div>
      </div>
    );
  }

  const formatDate = (dateStr: string) => {
    const [year, month, day] = dateStr.split('-');
    return `${day}/${month}/${year}`;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          Resumenes Mensuales
        </h1>
        
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="includeFuture"
            checked={includeFuture}
            onChange={(e) => setIncludeFuture(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <label htmlFor="includeFuture" className="text-sm text-gray-700">
            Mostrar resumenes futuros
          </label>
        </div>
      </div>

      {!statements || statements.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">
            No hay resumenes {includeFuture ? '' : 'pasados'} disponibles.
          </p>
          <p className="text-gray-400 text-sm mt-2">
            Los resumenes se crean automáticamente cuando se realiza una compra.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {statements.map((statement) => (
            <Link
              key={statement.id}
              to={`/statements/${statement.id}`}
              className="block bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-4 border border-gray-200"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">
                    {statement.credit_card_name}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Vencimiento: {formatDate(statement.due_date)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">
                    Cierre: {formatDate(statement.closing_date)}
                  </p>
                  <svg
                    className="w-6 h-6 text-gray-400 mt-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
