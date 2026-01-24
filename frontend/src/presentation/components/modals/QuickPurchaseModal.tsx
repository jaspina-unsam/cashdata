import React from 'react';
import { usePaymentMethods } from '../../../application/hooks/usePaymentMethods';
import { useCategories } from '../../../application/hooks/useCategories';
import { useCreatePurchase } from '../../../application/hooks/usePurchases';
import { useActiveUser } from '../../../application/contexts/UserContext';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export const QuickPurchaseModal: React.FC<Props> = ({ isOpen, onClose }) => {
  const { activeUserId } = useActiveUser();
  const paymentMethodsQuery = usePaymentMethods(activeUserId!);
  const categoriesQuery = useCategories();
  const createMutation = useCreatePurchase();

  const [amount, setAmount] = React.useState<number>(0);
  const [currency, setCurrency] = React.useState<'USD' | 'ARS'>('USD');
  const [paymentMethodId, setPaymentMethodId] = React.useState<number | undefined>(undefined);
  const [categoryId, setCategoryId] = React.useState<number | undefined>(undefined);
  const [description, setDescription] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeUserId) return alert('Seleccioná un usuario');
    if (!paymentMethodId) return alert('Seleccioná un método de pago');
    if (amount <= 0) return alert('El monto debe ser mayor a 0');

    setIsSubmitting(true);
    try {
      await createMutation.mutateAsync({ userId: activeUserId, data: {
        description,
        total_amount: amount,
        currency,
        payment_method_id: paymentMethodId,
        category_id: categoryId || 0,
        purchase_date: new Date().toISOString().split('T')[0],
        installments_count: 1,
      }});
      alert('Compra rápida creada');
      // TODO: invalidate queries - handled by mutation onSuccess
      onClose();
    } catch (err) {
      console.error(err);
      alert('Error creando la compra');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/30">
      <div className="bg-white rounded-lg p-6 w-full max-w-lg">
        <h2 className="text-lg font-semibold mb-4">Nueva Compra Rápida</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-sm">Descripción</label>
            <input type="text" value={description} onChange={e => setDescription(e.target.value)} className="w-full border rounded px-2 py-1" />
          </div>
          <div className="grid grid-cols-2 gap-3">
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
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm">Tarjeta</label>
              <select value={paymentMethodId} onChange={e => setPaymentMethodId(Number(e.target.value))} className="w-full border rounded px-2 py-1">
                <option value={0}>Seleccionar</option>
                {paymentMethodsQuery.data?.map(pm => (
                  <option key={pm.id} value={pm.id}>{pm.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm">Categoría</label>
              <select value={categoryId} onChange={e => setCategoryId(Number(e.target.value))} className="w-full border rounded px-2 py-1">
                <option value={0}>Seleccionar</option>
                {categoriesQuery.data?.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <button type="button" className="px-3 py-1 border rounded" onClick={onClose}>Cancelar</button>
            <button type="submit" className="px-3 py-1 bg-blue-600 text-white rounded" disabled={isSubmitting}>{isSubmitting ? 'Guardando...' : 'Crear y salir'}</button>
          </div>
        </form>
      </div>
    </div>
  );
};
