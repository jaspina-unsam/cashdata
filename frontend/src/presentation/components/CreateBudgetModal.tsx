import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useCreateBudget } from '../../application/hooks/useBudgets';
import { useUsers } from '../../application/hooks/useUsers';
import type { CreateBudgetData } from '../../infrastructure/api/budgetsRepository';

interface CreateBudgetModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentUserId: number;
}

export const CreateBudgetModal: React.FC<CreateBudgetModalProps> = ({
  isOpen,
  onClose,
  currentUserId,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    participant_user_ids: [currentUserId], // Creator is always included
  });

  const { data: users } = useUsers();
  const createBudget = useCreateBudget();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validations
    if (formData.name.trim().length === 0) {
      alert('El nombre es requerido');
      return;
    }

    if (formData.participant_user_ids.length === 0) {
      alert('Debe haber al menos un participante');
      return;
    }

    if (!formData.participant_user_ids.includes(currentUserId)) {
      alert('El creador debe ser un participante del presupuesto');
      return;
    }

    const budgetData: CreateBudgetData = {
      name: formData.name.trim(),
      description: formData.description.trim() || undefined,
      created_by_user_id: currentUserId,
      participant_user_ids: formData.participant_user_ids,
    };

    try {
      await createBudget.mutateAsync(budgetData);
      onClose();
      // Reset form
      setFormData({
        name: '',
        description: '',
        participant_user_ids: [currentUserId],
      });
    } catch (error: any) {
      alert(`Error al crear presupuesto: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleParticipantToggle = (userId: number) => {
    if (formData.participant_user_ids.includes(userId)) {
      // Don't allow removing the creator
      if (userId === currentUserId) {
        alert('El creador no puede ser removido de los participantes');
        return;
      }
      setFormData({
        ...formData,
        participant_user_ids: formData.participant_user_ids.filter((id) => id !== userId),
      });
    } else {
      setFormData({
        ...formData,
        participant_user_ids: [...formData.participant_user_ids, userId],
      });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Crear Presupuesto</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre del presupuesto *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ej: Gastos del hogar"
              required
              maxLength={100}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción (opcional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Describe el propósito del presupuesto..."
              rows={3}
              maxLength={500}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Participantes *
            </label>
            <div className="space-y-2 max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-3">
              {users?.map((user) => (
                <label
                  key={user.id}
                  className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded"
                >
                  <input
                    type="checkbox"
                    checked={formData.participant_user_ids.includes(user.id)}
                    onChange={() => handleParticipantToggle(user.id)}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">
                    {user.name}
                    {user.id === currentUserId && (
                      <span className="ml-2 text-xs text-blue-600 font-medium">(Tú - Creador)</span>
                    )}
                  </span>
                </label>
              ))}
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Selecciona quiénes participarán en este presupuesto. El creador siempre debe estar incluido.
            </p>
          </div>

          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createBudget.isPending}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-blue-400 disabled:cursor-not-allowed"
            >
              {createBudget.isPending ? 'Creando...' : 'Crear Presupuesto'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
