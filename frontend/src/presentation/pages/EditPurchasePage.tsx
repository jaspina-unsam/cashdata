import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePurchase, useUpdatePurchase } from '../../application/hooks/usePurchases';
import InstallmentEditor from '../components/InstallmentEditor';
import { useCategories } from '../../application/hooks/useCategories';
import { useCreditCards } from '../../application/hooks/useCreditCards';

const CURRENT_USER_ID = 1;

export default function EditPurchasePage() {
  const { id } = useParams();
  const purchaseId = Number(id);
  const navigate = useNavigate();

  const { data: purchase, isLoading, error } = usePurchase(purchaseId, CURRENT_USER_ID);
  const { data: categories } = useCategories();
  const { data: creditCards } = useCreditCards(CURRENT_USER_ID);

  const updatePurchase = useUpdatePurchase();

  const [form, setForm] = useState<any>(null);

  useEffect(() => {
    if (purchase) {
      setForm({
        description: purchase.description,
        category_id: purchase.category_id,
        purchase_date: purchase.purchase_date,
        total_amount: String(purchase.total_amount),
      });
    }
  }, [purchase]);

  if (isLoading || !form) return <div>Cargando...</div>;
  if (error) return <div>Error al cargar compra</div>;

  const onSave = async () => {
    try {
      await updatePurchase.mutateAsync({ id: purchaseId, userId: CURRENT_USER_ID, data: {
        description: form.description,
        category_id: Number(form.category_id),
        purchase_date: form.purchase_date,
        total_amount: Number(form.total_amount),
      }});
      navigate('/purchases');
    } catch (err: any) {
      alert(`Error al actualizar: ${err?.message || 'Error desconocido'}`);
    }
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <button onClick={() => navigate('/purchases')} className="text-blue-600">← Volver</button>
        <h2 className="text-2xl font-semibold">Editar Compra</h2>
        <div />
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-700">Descripción</label>
            <input className="mt-1 w-full" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm text-gray-700">Categoría</label>
            <select className="mt-1 w-full" value={form.category_id} onChange={(e) => setForm({ ...form, category_id: Number(e.target.value) })}>
              {categories?.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-700">Fecha de compra</label>
            <input type="date" className="mt-1 w-full" value={form.purchase_date} onChange={(e) => setForm({ ...form, purchase_date: e.target.value })} />
          </div>
          {purchase.installments_count === 1 && (
            <div>
              <label className="block text-sm text-gray-700">Monto total</label>
              <input type="number" className="mt-1 w-full" value={form.total_amount} onChange={(e) => setForm({ ...form, total_amount: e.target.value })} />
            </div>
          )}
        </div>

        <div className="mt-6 flex gap-3">
          <button onClick={onSave} className="bg-blue-600 text-white px-4 py-2 rounded">Guardar cambios</button>
          <button onClick={() => navigate('/purchases')} className="bg-gray-200 px-4 py-2 rounded">Cancelar</button>
        </div>
      </div>

      {/* Installments editor for multi-installment purchases */}
      {purchase.installments_count > 1 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold">Cuotas</h3>
          <InstallmentEditor purchaseId={purchaseId} userId={CURRENT_USER_ID} creditCardId={purchase.credit_card_id} />
        </div>
      )}
    </div>
  );
}
