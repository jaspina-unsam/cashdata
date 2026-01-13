import ConfirmDialog from './ConfirmDialog';
import { useDeletePurchase } from '../../application/hooks/usePurchases';

type Props = {
  purchaseId: number | null;
  isOpen: boolean;
  onClose: () => void;
  description?: string;
  userId: number;
};

export function DeletePurchaseModal({ purchaseId, isOpen, onClose, description, userId }: Props) {
  const deleteMutation = useDeletePurchase();

  const handleConfirm = async () => {
    if (!purchaseId) return;
    try {
      await deleteMutation.mutateAsync({ id: purchaseId, userId });
      onClose();
    } catch (err: any) {
      console.error('Delete failed', err);
      alert(`Error al eliminar compra: ${err?.message || 'Error desconocido'}`);
    }
  };

  return (
    <ConfirmDialog
      isOpen={isOpen}
      title="Eliminar compra"
      description={description || '¿Querés eliminar esta compra? Esta acción no se puede deshacer.'}
      confirmLabel="Eliminar"
      cancelLabel="Cancelar"
      onCancel={onClose}
      onConfirm={handleConfirm}
    />
  );
}

export default DeletePurchaseModal;
