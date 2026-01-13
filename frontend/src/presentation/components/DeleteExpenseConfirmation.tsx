import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

interface DeleteExpenseConfirmationProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  expenseDescription: string;
  isDeleting: boolean;
}

export const DeleteExpenseConfirmation: React.FC<DeleteExpenseConfirmationProps> = ({
  isOpen,
  onClose,
  onConfirm,
  expenseDescription,
  isDeleting,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">Eliminar Gasto</h3>
              <p className="text-sm text-gray-500 mt-1">Esta acción no se puede deshacer</p>
            </div>
            <button
              onClick={onClose}
              disabled={isDeleting}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="mb-6">
            <p className="text-gray-700">
              ¿Estás seguro que querés eliminar este gasto del presupuesto?
            </p>
            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-900">{expenseDescription}</p>
            </div>
            <p className="text-sm text-gray-600 mt-3">
              Se eliminarán todas las responsabilidades asociadas y se recalcularán los balances.
            </p>
          </div>

          <div className="flex justify-end gap-3">
            <button
              onClick={onClose}
              disabled={isDeleting}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              onClick={onConfirm}
              disabled={isDeleting}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isDeleting ? 'Eliminando...' : 'Eliminar Gasto'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
