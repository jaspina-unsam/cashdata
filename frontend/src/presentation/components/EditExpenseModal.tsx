import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { useUpdateResponsibilities } from '../../application/hooks/useBudgets';

interface EditExpenseModalProps {
  isOpen: boolean;
  onClose: () => void;
  budgetId: number;
  expenseId: number;
  currentUserId: number;
  currentSplitType: 'equal' | 'proportional' | 'custom' | 'full_single';
  participants: Array<{ id: number; name: string }>;
  expenseDescription: string;
}

export const EditExpenseModal: React.FC<EditExpenseModalProps> = ({
  isOpen,
  onClose,
  budgetId,
  expenseId,
  currentUserId,
  currentSplitType,
  participants,
  expenseDescription,
}) => {
  const [splitType, setSplitType] = useState<'equal' | 'proportional' | 'custom' | 'full_single'>(currentSplitType);
  const [customPercentages, setCustomPercentages] = useState<Record<number, string>>({});
  const [responsibleUserId, setResponsibleUserId] = useState<number | null>(null);

  const updateMutation = useUpdateResponsibilities();

  // Initialize form when modal opens
  useEffect(() => {
    if (isOpen) {
      setSplitType(currentSplitType);
      if (currentSplitType === 'custom') {
        const initialPercentages: Record<number, string> = {};
        participants.forEach((p) => {
          initialPercentages[p.id] = '';
        });
        setCustomPercentages(initialPercentages);
      }
    }
  }, [isOpen, currentSplitType, participants]);

  if (!isOpen) return null;

  const handleSubmit = async () => {
    if (splitType === 'custom') {
      const percentages: Record<number, number> = {};
      let total = 0;

      for (const participant of participants) {
        const value = parseFloat(customPercentages[participant.id] || '0');
        if (isNaN(value) || value < 0 || value > 100) {
          alert(`Porcentaje inválido para ${participant.name}`);
          return;
        }
        percentages[participant.id] = value;
        total += value;
      }

      if (Math.abs(total - 100) > 0.01) {
        alert(`Los porcentajes deben sumar 100% (actual: ${total.toFixed(1)}%)`);
        return;
      }

      try {
        await updateMutation.mutateAsync({
          budgetId,
          expenseId,
          data: {
            budget_expense_id: expenseId,
            split_type: splitType,
            custom_percentages: percentages,
            requesting_user_id: currentUserId,
          },
        });
        onClose();
      } catch (error) {
        console.error('Error updating expense:', error);
        alert('Error al actualizar el gasto');
      }
    } else if (splitType === 'full_single') {
      if (!responsibleUserId) {
        alert('Por favor selecciona quién es responsable del 100%');
        return;
      }

      try {
        await updateMutation.mutateAsync({
          budgetId,
          expenseId,
          data: {
            budget_expense_id: expenseId,
            split_type: splitType,
            responsible_user_id: responsibleUserId,
            requesting_user_id: currentUserId,
          },
        });
        onClose();
      } catch (error) {
        console.error('Error updating expense:', error);
        alert('Error al actualizar el gasto');
      }
    } else {
      // equal or proportional
      try {
        await updateMutation.mutateAsync({
          budgetId,
          expenseId,
          data: {
            budget_expense_id: expenseId,
            split_type: splitType,
            requesting_user_id: currentUserId,
          },
        });
        onClose();
      } catch (error) {
        console.error('Error updating expense:', error);
        alert('Error al actualizar el gasto');
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Editar División del Gasto</h2>
            <p className="text-sm text-gray-600 mt-1">{expenseDescription}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={updateMutation.isPending}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Split Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de División
            </label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="splitType"
                  value="equal"
                  checked={splitType === 'equal'}
                  onChange={(e) => setSplitType(e.target.value as any)}
                  className="w-4 h-4 text-blue-600"
                />
                <div>
                  <div className="font-medium">50/50 (Partes iguales)</div>
                  <div className="text-sm text-gray-500">Cada participante paga lo mismo</div>
                </div>
              </label>

              <label className="flex items-center gap-2 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="splitType"
                  value="proportional"
                  checked={splitType === 'proportional'}
                  onChange={(e) => setSplitType(e.target.value as any)}
                  className="w-4 h-4 text-blue-600"
                />
                <div>
                  <div className="font-medium">Proporcional (según ingresos)</div>
                  <div className="text-sm text-gray-500">División según salarios configurados</div>
                </div>
              </label>

              <label className="flex items-center gap-2 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="splitType"
                  value="custom"
                  checked={splitType === 'custom'}
                  onChange={(e) => setSplitType(e.target.value as any)}
                  className="w-4 h-4 text-blue-600"
                />
                <div>
                  <div className="font-medium">Personalizado</div>
                  <div className="text-sm text-gray-500">Define porcentajes manualmente</div>
                </div>
              </label>

              <label className="flex items-center gap-2 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="splitType"
                  value="full_single"
                  checked={splitType === 'full_single'}
                  onChange={(e) => setSplitType(e.target.value as any)}
                  className="w-4 h-4 text-blue-600"
                />
                <div>
                  <div className="font-medium">100% una persona</div>
                  <div className="text-sm text-gray-500">Todo el gasto para un solo participante</div>
                </div>
              </label>
            </div>
          </div>

          {/* Custom percentages input */}
          {splitType === 'custom' && (
            <div className="border rounded-lg p-4 bg-gray-50">
              <div className="text-sm font-medium text-gray-700 mb-3">
                Porcentajes Personalizados (deben sumar 100%)
              </div>
              <div className="space-y-3">
                {participants.map((participant) => (
                  <div key={participant.id} className="flex items-center gap-3">
                    <label className="flex-1 text-sm text-gray-700">{participant.name}</label>
                    <div className="flex items-center gap-1">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="0.01"
                        value={customPercentages[participant.id] || ''}
                        onChange={(e) =>
                          setCustomPercentages({
                            ...customPercentages,
                            [participant.id]: e.target.value,
                          })
                        }
                        className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="0"
                      />
                      <span className="text-gray-600">%</span>
                    </div>
                  </div>
                ))}
                <div className="pt-2 border-t text-sm">
                  <span className="text-gray-600">Total: </span>
                  <span className="font-medium">
                    {Object.values(customPercentages)
                      .reduce((sum, val) => sum + (parseFloat(val) || 0), 0)
                      .toFixed(1)}
                    %
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Responsible user selection for full_single */}
          {splitType === 'full_single' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Persona Responsable (100%)
              </label>
              <select
                value={responsibleUserId || ''}
                onChange={(e) => setResponsibleUserId(parseInt(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Seleccionar participante</option>
                {participants.map((participant) => (
                  <option key={participant.id} value={participant.id}>
                    {participant.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 px-6 py-4 border-t flex justify-end gap-3">
          <button
            onClick={onClose}
            disabled={updateMutation.isPending}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={updateMutation.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {updateMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}
          </button>
        </div>
      </div>
    </div>
  );
};
