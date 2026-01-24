import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePurchase, useUpdatePurchase } from '../../application/hooks/usePurchases';
import InstallmentEditor from '../components/InstallmentEditor';
import { useCategories } from '../../application/hooks/useCategories';
import { useExchangeRates } from '../../application/hooks/useExchangeRates';
import { usePaymentMethods } from '../../application/hooks/usePaymentMethods';
import { useCreditCards } from '../../application/hooks/useCreditCards';

import { useActiveUser } from '../../application/contexts/UserContext';


export default function EditPurchasePage() {
  const { id } = useParams();
  const purchaseId = Number(id);
  const navigate = useNavigate();

  const { activeUserId } = useActiveUser();
  const { data: purchase, isLoading, error } = usePurchase(purchaseId, activeUserId);
  const { data: categories } = useCategories();
  const { data: paymentMethods } = usePaymentMethods(activeUserId);
  const { data: creditCards } = useCreditCards(activeUserId);
  
  // Fetch exchange rates - get all available rates to allow flexibility in selection
  const { data: exchangeRates } = useExchangeRates(activeUserId, {});

  const updatePurchase = useUpdatePurchase();

  const [form, setForm] = useState<any>(null);

  useEffect(() => {
    if (purchase) {
      setForm({
        description: purchase.description,
        category_id: purchase.category_id,
        purchase_date: purchase.purchase_date,
        total_amount: String(purchase.total_amount),
        currency: purchase.currency || 'ARS',
        original_amount: purchase.original_amount ? String(purchase.original_amount) : '',
        original_currency: purchase.original_currency || '',
        exchange_rate_id: purchase.exchange_rate_id || null,
      });
    }
  }, [purchase]);

  if (isLoading || !form) return <div>Cargando...</div>;
  if (error) return <div>Error al cargar compra</div>;

  const onSave = async () => {
    try {
      // Update purchase with dual-currency fields
      await updatePurchase.mutateAsync({ 
        id: purchaseId, 
        userId: activeUserId, 
        data: {
          description: form.description,
          category_id: Number(form.category_id),
          purchase_date: form.purchase_date,
          total_amount: Number(form.total_amount),
          original_amount: form.original_amount ? Number(form.original_amount) : undefined,
          original_currency: form.original_currency || undefined,
          exchange_rate_id: (form.exchange_rate_id && form.exchange_rate_id !== 'custom') ? Number(form.exchange_rate_id) : undefined,
        }
      });
      
      navigate('/purchases');
    } catch (err: any) {
      alert(`Error al actualizar: ${err?.message || 'Error desconocido'}`);
    }
  };

  return (
    <div>
      <div className="mb-4 flex items-center gap-4">
        <button onClick={() => navigate('/purchases')} className="text-blue-600">← Volver</button>
        <h2 className="text-2xl font-semibold">Editar Compra</h2>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
            <input className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
            <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" value={form.category_id} onChange={(e) => setForm({ ...form, category_id: Number(e.target.value) })}>
              {categories?.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de compra</label>
            <input 
              type="date" 
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
              value={form.purchase_date} 
              onChange={(e) => setForm({ ...form, purchase_date: e.target.value })} 
            />
          </div>
          {purchase && purchase.installments_count === 1 && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Monto ({form.currency})</label>
                <input type="number" step="0.01" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" value={form.total_amount} onChange={(e) => setForm({ ...form, total_amount: e.target.value })} />
              </div>
              
              {/* Dual-currency fields */}
              <div className="md:col-span-2">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Conversión de moneda (opcional)</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">
                      Monto en {form.currency === 'USD' ? 'ARS' : 'USD'}
                    </label>
                    <input 
                      type="number" 
                      step="0.01"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
                      value={form.original_amount} 
                      onChange={(e) => {
                        const newAmount = e.target.value;
                        setForm({ 
                          ...form, 
                          original_amount: newAmount,
                          original_currency: form.currency === 'USD' ? 'ARS' : 'USD',
                          exchange_rate_id: newAmount ? 'custom' : null
                        });
                      }} 
                      placeholder={form.currency === 'USD' ? 'Ej: 150000.00' : 'Ej: 100.00'}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">Tipo de cambio</label>
                    <select 
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
                      value={form.exchange_rate_id || ''} 
                      onChange={(e) => {
                        const selectedValue = e.target.value;
                        if (selectedValue === 'custom' || selectedValue === '') {
                          setForm({ ...form, exchange_rate_id: selectedValue || null });
                        } else {
                          // Caso A: Seleccionar tipo de cambio existente → auto-calcular monto
                          const selectedRate = exchangeRates?.find((r: any) => r.id === Number(selectedValue));
                          if (selectedRate && form.total_amount) {
                            const calculatedAmount = (Number(form.total_amount) * Number(selectedRate.rate)).toFixed(2);
                            setForm({ 
                              ...form, 
                              exchange_rate_id: Number(selectedValue),
                              original_amount: calculatedAmount,
                              original_currency: form.currency === 'USD' ? 'ARS' : 'USD'
                            });
                          } else {
                            setForm({ ...form, exchange_rate_id: Number(selectedValue) });
                          }
                        }
                      }}
                    >
                      <option value="">Seleccionar tipo de cambio...</option>
                      {form.original_amount && form.exchange_rate_id === 'custom' && (
                        <option value="custom">Monto personalizado</option>
                      )}
                      {exchangeRates?.filter((rate: any) => 
                        (form.currency === 'USD' && rate.from_currency === 'USD' && rate.to_currency === 'ARS') ||
                        (form.currency === 'ARS' && rate.from_currency === 'ARS' && rate.to_currency === 'USD')
                      ).sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime())
                      .map((rate: any) => (
                        <option key={rate.id} value={rate.id}>
                          {new Date(rate.date).toLocaleDateString('es-AR')} - {rate.rate_type}: {Number(rate.rate).toFixed(2)}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">Vista previa</label>
                    <div className="w-full px-4 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm">
                      {form.original_amount && form.total_amount ? (
                        <>
                          1 {form.currency} = {
                            form.exchange_rate_id === 'custom' 
                              ? (Number(form.original_amount) / Number(form.total_amount)).toFixed(2)
                              : (exchangeRates?.find((r: any) => r.id === form.exchange_rate_id)?.rate 
                                  ? Number(exchangeRates?.find((r: any) => r.id === form.exchange_rate_id)?.rate).toFixed(2)
                                  : '0.00')
                          } {form.currency === 'USD' ? 'ARS' : 'USD'}
                        </>
                      ) : (
                        <span className="text-gray-400">Completá los campos</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="mt-6 flex gap-3">
          <button onClick={onSave} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">Guardar cambios</button>
          <button onClick={() => navigate('/purchases')} className="bg-gray-200 hover:bg-gray-300 px-4 py-2 rounded-lg transition-colors">Cancelar</button>
        </div>
      </div>

      {/* Installments editor for credit card purchases */}
      {purchase && paymentMethods && creditCards && (() => {
        const paymentMethod = paymentMethods.find(pm => pm.id === purchase.payment_method_id);
        const isCreditCard = paymentMethod?.type === 'credit_card';
        if (!isCreditCard) return null;
        
        // Find the credit card that corresponds to this payment method
        const creditCard = creditCards.find(cc => cc.payment_method_id === purchase.payment_method_id);
        
        console.log('Credit card lookup:', {
          purchasePaymentMethodId: purchase.payment_method_id,
          allCreditCards: creditCards,
          foundCreditCard: creditCard
        });
        
        if (!creditCard) {
          console.error('No credit card found for payment_method_id:', purchase.payment_method_id);
          return null;
        }
        
        return (
          <div className="mt-6">
            <h3 className="text-lg font-semibold">Cuotas</h3>
            <InstallmentEditor 
              purchaseId={purchaseId} 
              userId={activeUserId} 
              creditCardId={creditCard.id}
            />
          </div>
        );
      })()}
    </div>
  );
}
