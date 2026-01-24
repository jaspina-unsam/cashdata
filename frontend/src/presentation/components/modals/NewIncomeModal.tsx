import React from 'react';
import { httpClient } from '../../../infrastructure/http/httpClient';
import { useActiveUser } from '../../../application/contexts/UserContext';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export const NewIncomeModal: React.FC<Props> = ({ isOpen, onClose }) => {
  const { activeUserId } = useActiveUser();
  const [amount, setAmount] = React.useState<number>(0);
  const [currency, setCurrency] = React.useState<'USD' | 'ARS'>('USD');
  const [description, setDescription] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeUserId) return alert('Seleccioná un usuario');
    if (amount <= 0) return alert('El monto debe ser mayor a 0');

    setIsSubmitting(true);
    try {
      await httpClient.post('/api/v1/monthly-incomes', {
        amount,
        currency,
        description,
      }, { user_id: activeUserId });
      alert('Ingreso agregado correctamente');
      // TODO: invalidate queries (dashboard metrics) - requires queryClient access
      onClose();
    } catch (err) {
      console.error(err);
      alert('Error al crear el ingreso');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/30">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-lg font-semibold mb-4">Nuevo Ingreso</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-sm">Monto</label>
            <input type="number" value={amount} onChange={e => setAmount(Number(e.target.value))} className="w-full border rounded px-2 py-1" />
          </div>
          <div>
            <label className="block text-sm">Moneda</label>
            <select value={currency} onChange={e => setCurrency(e.target.value as 'USD' | 'ARS')} className="w-full border rounded px-2 py-1">
              <option value="USD">USD</option>
              <option value="ARS">ARS</option>
            </select>
          </div>
          <div>
            <label className="block text-sm">Descripción (opcional)</label>
            <input type="text" value={description} onChange={e => setDescription(e.target.value)} className="w-full border rounded px-2 py-1" />
          </div>

          <div className="flex justify-end gap-2">
            <button type="button" className="px-3 py-1 border rounded" onClick={onClose}>Cancelar</button>
            <button type="submit" className="px-3 py-1 bg-green-600 text-white rounded" disabled={isSubmitting}>{isSubmitting ? 'Guardando...' : 'Guardar'}</button>
          </div>
        </form>
      </div>
    </div>
  );
};
