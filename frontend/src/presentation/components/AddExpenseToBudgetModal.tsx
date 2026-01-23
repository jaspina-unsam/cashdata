import React, { useState, useEffect } from 'react';
import { X, Search } from 'lucide-react';
import { useAddExpense } from '../../application/hooks/useBudgets';
import { usePurchases, usePurchaseInstallments } from '../../application/hooks/usePurchases';

interface AddExpenseToBudgetModalProps {
  isOpen: boolean;
  onClose: () => void;
  budgetId: number;
  currentUserId: number;
  participants: Array<{ id: number; name: string }>;
}

export const AddExpenseToBudgetModal: React.FC<AddExpenseToBudgetModalProps> = ({
  isOpen,
  onClose,
  budgetId,
  currentUserId,
  participants,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPurchaseId, setSelectedPurchaseId] = useState<number | null>(null);
  const [selectedInstallmentId, setSelectedInstallmentId] = useState<number | null>(null);
  const [splitType, setSplitType] = useState<'equal' | 'proportional' | 'custom' | 'full_single'>('equal');
  const [customPercentages, setCustomPercentages] = useState<Record<number, string>>({});
  const [responsibleUserId, setResponsibleUserId] = useState<number | null>(null);
  const [expandedPurchases, setExpandedPurchases] = useState<Set<number>>(new Set());

  const addExpenseMutation = useAddExpense();

  // Fetch all purchases (no date restrictions)
  const { data: purchasesData } = usePurchases(currentUserId);
  const purchases = purchasesData?.items || [];

  // Initialize custom percentages when participants change
  useEffect(() => {
    if (splitType === 'custom') {
      const initialPercentages: Record<number, string> = {};
      participants.forEach((p) => {
        initialPercentages[p.id] = customPercentages[p.id] || '';
      });
      setCustomPercentages(initialPercentages);
    }
  }, [participants, splitType]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setSearchQuery('');
      setSelectedPurchaseId(null);
      setSelectedInstallmentId(null);
      setSplitType('equal');
      setCustomPercentages({});
      setResponsibleUserId(null);
      setExpandedPurchases(new Set());
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async () => {
    // Validation
    if (!selectedPurchaseId && !selectedInstallmentId) {
      alert('Por favor selecciona un gasto o cuota');
      return;
    }

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
        await addExpenseMutation.mutateAsync({
          budget_id: budgetId,
          purchase_id: selectedPurchaseId || undefined,
          installment_id: selectedInstallmentId || undefined,
          split_type: splitType,
          custom_percentages: percentages,
          requesting_user_id: currentUserId,
        });
        onClose();
      } catch (error) {
        console.error('Error adding expense:', error);
        alert('Error al agregar el gasto');
      }
    } else if (splitType === 'full_single') {
      if (!responsibleUserId) {
        alert('Por favor selecciona quién es responsable del 100%');
        return;
      }

      try {
        await addExpenseMutation.mutateAsync({
          budget_id: budgetId,
          purchase_id: selectedPurchaseId || undefined,
          installment_id: selectedInstallmentId || undefined,
          split_type: splitType,
          responsible_user_id: responsibleUserId,
          requesting_user_id: currentUserId,
        });
        onClose();
      } catch (error: any) {
        console.error('Error adding expense:', error);
        console.error('Error details:', error.errorData);
        alert(`Error al agregar el gasto: ${error.message || JSON.stringify(error.errorData)}`);
      }
    } else {
      // equal or proportional
      try {
        await addExpenseMutation.mutateAsync({
          budget_id: budgetId,
          purchase_id: selectedPurchaseId || undefined,
          installment_id: selectedInstallmentId || undefined,
          split_type: splitType,
          requesting_user_id: currentUserId,
        });
        onClose();
      } catch (error: any) {
        console.error('Error adding expense:', error);
        console.error('Error details:', error.errorData);
        alert(`Error al agregar el gasto: ${error.message || JSON.stringify(error.errorData)}`);
      }
    }
  };

  const filteredPurchases = purchases.filter((p) =>
    p.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const togglePurchaseExpansion = (purchaseId: number) => {
    const newExpanded = new Set(expandedPurchases);
    if (newExpanded.has(purchaseId)) {
      newExpanded.delete(purchaseId);
    } else {
      newExpanded.add(purchaseId);
    }
    setExpandedPurchases(newExpanded);
  };

  const handlePurchaseSelect = (purchaseId: number) => {
    setSelectedPurchaseId(purchaseId);
    setSelectedInstallmentId(null);
  };

  const handleInstallmentSelect = (installmentId: number) => {
    setSelectedInstallmentId(installmentId);
    setSelectedPurchaseId(null);
  };

  // Component for rendering installments
  const InstallmentsList: React.FC<{ purchaseId: number }> = ({ purchaseId }) => {
    const { data: installments, isLoading } = usePurchaseInstallments(purchaseId, currentUserId);

    if (isLoading) {
      return (
        <div className="ml-7 mt-2 pl-4 border-l-2 border-gray-200">
          <div className="text-sm text-gray-500">Cargando cuotas...</div>
        </div>
      );
    }

    if (!installments || installments.length === 0) {
      return null;
    }

    return (
      <div className="ml-7 mt-2 space-y-2 pl-4 border-l-2 border-gray-200">
        {installments.map((installment) => (
          <div key={installment.id} className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded">
            <input
              type="radio"
              name="expense"
              checked={selectedInstallmentId === installment.id}
              onChange={() => handleInstallmentSelect(installment.id)}
              className="w-4 h-4 text-blue-600"
            />
            <div className="flex-1">
              <div className="text-sm text-gray-900">
                Cuota {installment.installment_number}/{installment.total_installments}
              </div>
              <div className="text-xs text-gray-500">
                ${installment.amount} {installment.currency} • {installment.billing_period}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">Agregar Gasto al Presupuesto</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={addExpenseMutation.isPending}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Search expenses */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Buscar Compras/Cuotas del Período
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar por descripción..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Expense list */}
          <div className="border rounded-lg max-h-60 overflow-y-auto">
            {filteredPurchases.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No hay compras en este período
              </div>
            ) : (
              <div className="divide-y">
                {filteredPurchases.map((purchase) => {
                  const isExpanded = expandedPurchases.has(purchase.id);
                  const hasInstallments = purchase.installments_count > 1;

                  return (
                    <div key={purchase.id} className="p-3">
                      <div className="flex items-center gap-3">
                        <input
                          type="radio"
                          name="expense"
                          checked={selectedPurchaseId === purchase.id}
                          onChange={() => handlePurchaseSelect(purchase.id)}
                          className="w-4 h-4 text-blue-600"
                        />
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{purchase.description}</div>
                          <div className="text-sm text-gray-500">
                            {purchase.purchase_date} • ${purchase.total_amount} {purchase.currency}
                            {hasInstallments && ` • ${purchase.installments_count} cuotas`}
                          </div>
                        </div>
                        {hasInstallments && (
                          <button
                            onClick={() => togglePurchaseExpansion(purchase.id)}
                            className="text-blue-600 text-sm hover:underline"
                          >
                            {isExpanded ? 'Ocultar cuotas' : 'Ver cuotas'}
                          </button>
                        )}
                      </div>

                      {/* Installments */}
                      {isExpanded && hasInstallments && (
                        <InstallmentsList purchaseId={purchase.id} />
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

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
            disabled={addExpenseMutation.isPending}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={addExpenseMutation.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {addExpenseMutation.isPending ? 'Agregando...' : 'Agregar Gasto'}
          </button>
        </div>
      </div>
    </div>
  );
};
