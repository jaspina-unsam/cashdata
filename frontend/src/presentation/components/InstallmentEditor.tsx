import React, { useState } from 'react';
import { usePurchaseInstallments, usePurchaseInstallmentsMutation } from '../../application/hooks/useInstallments';
import { useStatements } from '../../application/hooks/useStatements';

type Props = {
  purchaseId: number;
  userId: number;
};

export function InstallmentEditor({ purchaseId, userId }: Props) {
  const { data: installments, isLoading } = usePurchaseInstallments(purchaseId, userId);
  const statementsQuery = useStatements(userId, true);
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
    // basic validation
    const amount = parseFloat(entry.amount);
    if (isNaN(amount) || amount === 0) {
      alert('El monto de la cuota no puede ser cero');
      return;
    }

    try {
      await updateMutation.mutateAsync({ id: instId, userId, data: { amount: amount, manually_assigned_statement_id: entry.statementId ?? null } });
      alert('Cuota actualizada');
    } catch (err: any) {
      console.error('Update installment failed', err);
      alert(`Error al actualizar cuota: ${err?.message || 'Error desconocido'}`);
    }
  };

  return (
    <div className="mt-3 space-y-3">
      {installments.map((inst: any) => (
        <div key={inst.id} className="bg-white p-3 rounded shadow-sm grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
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
              <button onClick={() => handleSave(inst.id)} className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">Guardar</button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default InstallmentEditor;
