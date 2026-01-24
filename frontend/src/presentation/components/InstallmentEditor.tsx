import React, { useState } from 'react';
import { usePurchaseInstallments, usePurchaseInstallmentsMutation } from '../../application/hooks/useInstallments';
import { useStatementsByCard } from '../../application/hooks/useStatements';

type Props = {
  purchaseId: number;
  userId: number;
  creditCardId: number;
};

export function InstallmentEditor({ purchaseId, userId, creditCardId }: Props) {
  const { data: installments, isLoading } = usePurchaseInstallments(purchaseId, userId);
  const statementsQuery = useStatementsByCard(creditCardId, userId);
  const updateMutation = usePurchaseInstallmentsMutation();

  const [local, setLocal] = useState<Record<number, { amount: string; statementId?: number | null }>>({});

  const prepare = () => {
    if (!installments) return;
    const map: Record<number, { amount: string; statementId?: number | null }> = {};
    installments.forEach((inst: any) => {
      map[inst.id] = { amount: String(inst.amount), statementId: inst.manually_assigned_statement_id ?? null };
    });
    setLocal(map);
  };

  React.useEffect(() => {
    prepare();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [installments]);

  if (isLoading) return <div>Cargando cuotas...</div>;
  if (!installments) return <div>No hay cuotas</div>;

  const handleChange = (instId: number, field: 'amount' | 'statementId', value: any) => {
    setLocal((s) => ({ ...s, [instId]: { ...(s[instId] || {}), [field]: value } }));
  };

  const handleSave = async (instId: number) => {
    const entry = local[instId];
    if (!entry) return;
    
    // Find original installment to detect changes
    const originalInst = installments?.find((i: any) => i.id === instId);
    if (!originalInst) return;

    console.log('Original installment:', originalInst);
    console.log('Local entry:', entry);

    // Build data object with only changed fields
    const data: any = {};
    
    // Check if amount changed
    const newAmount = parseFloat(entry.amount);
    if (isNaN(newAmount) || newAmount === 0) {
      alert('El monto de la cuota no puede ser cero');
      return;
    }
    if (newAmount !== parseFloat(String(originalInst.amount))) {
      data.amount = newAmount;
    }
    
    // Check if statement assignment changed
    // Normalize values: treat undefined, null, and empty string as null
    const normalizeStatementId = (val: any) => {
      if (val === '' || val === null || val === undefined) return null;
      return Number(val);
    };
    
    const newStatementId = normalizeStatementId(entry.statementId);
    const originalStatementId = normalizeStatementId(originalInst.manually_assigned_statement_id);
    
    console.log('Statement comparison:', { 
      newStatementId, 
      originalStatementId,
      changed: newStatementId !== originalStatementId 
    });
    
    if (newStatementId !== originalStatementId) {
      data.manually_assigned_statement_id = newStatementId;
    }

    // If nothing changed, don't send request
    if (Object.keys(data).length === 0) {
      alert('No hay cambios para guardar');
      return;
    }

    console.log('Sending installment update:', { id: instId, userId, purchaseId, data });

    try {
      await updateMutation.mutateAsync({ id: instId, userId, purchaseId, data });
      alert('Cuota actualizada');
    } catch (err: any) {
      console.error('Update installment failed', err);
      alert(`Error al actualizar cuota: ${err?.message || 'Error desconocido'}`);
    }
  };

  return (
    <div className="mt-3 space-y-3" data-testid="installment-editor">
      {installments.map((inst: any) => (
        <div key={inst.id} data-testid="installment-row" className="bg-white p-3 rounded shadow-sm grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
          <div>
            <div className="text-sm text-gray-700">Cuota {inst.installment_number}/{inst.total_installments}</div>
            <div className="text-sm text-gray-500">Período {inst.billing_period}</div>
          </div>

          <div>
            <label className="block text-xs text-gray-600">Monto</label>
            <input
              type="number"
              step="0.01"
              className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={local[inst.id]?.amount ?? String(inst.amount)}
              onChange={(e) => handleChange(inst.id, 'amount', e.target.value)}
            />
          </div>

          <div className="flex items-end gap-2">
            <div className="flex-1">
              <label className="block text-xs text-gray-600">Asignación de resumen</label>
              <select
                data-testid="statement-selector"
                className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={local[inst.id]?.statementId ?? ''}
                onChange={(e) => handleChange(inst.id, 'statementId', e.target.value ? Number(e.target.value) : null)}
              >
                <option value="">Automático</option>
                {statementsQuery.data?.map((st: any) => (
                  <option key={st.id} value={st.id}>Asignar a Venc.: {st.due_date}</option>
                ))}
              </select>
            </div>

            <div>
              <button data-testid="save-installment-button" onClick={() => handleSave(inst.id)} className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">Guardar</button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default InstallmentEditor;
