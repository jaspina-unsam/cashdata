/**
 * Users Page
 * 
 * Displays list of users with ability to create new ones.
 */

import { useState } from 'react';
import { Plus, User as UserIcon, Mail, DollarSign } from 'lucide-react';
import { useUsers, useCreateUser } from '../../application';
import type { User } from '../../domain/entities';

export function UsersPage() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    wage_amount: '',
    wage_currency: 'ARS',
  });

  const { data: users, isLoading, error } = useUsers();
  const createUser = useCreateUser();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.name.trim() || !formData.email.trim() || !formData.wage_amount) {
      alert('Por favor completá todos los campos');
      return;
    }

    const amount = parseFloat(formData.wage_amount);
    if (amount <= 0) {
      alert('El salario debe ser mayor a 0');
      return;
    }

    try {
      const userData: Omit<User, 'id'> = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        wage_amount: formData.wage_amount,
        wage_currency: formData.wage_currency,
      };

      await createUser.mutateAsync(userData);
      
      // Reset form
      setFormData({
        name: '',
        email: '',
        wage_amount: '',
        wage_currency: 'ARS',
      });
      setShowForm(false);
    } catch (err: any) {
      console.error('Failed to create user:', err);
      alert(`Error al crear usuario: ${err.data?.detail || err.message || 'Error desconocido'}`);
    }
  };

  const handleCancel = () => {
    setFormData({
      name: '',
      email: '',
      wage_amount: '',
      wage_currency: 'ARS',
    });
    setShowForm(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Cargando usuarios...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-600">Error al cargar usuarios: {(error as Error).message}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Usuarios</h1>
              <p className="text-gray-600 mt-1">Gestioná los usuarios del sistema</p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Plus size={20} />
              Nuevo Usuario
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Create Form */}
        {showForm && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h2 className="text-xl font-semibold mb-4">Nuevo Usuario</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre Completo *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Ej: Juan Pérez"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="Ej: juan@example.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Wage Amount */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Salario Mensual *
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      value={formData.wage_amount}
                      onChange={(e) => setFormData({ ...formData, wage_amount: e.target.value })}
                      placeholder="50000.00"
                      step="0.01"
                      min="0.01"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    />
                    <select
                      value={formData.wage_currency}
                      onChange={(e) => setFormData({ ...formData, wage_currency: e.target.value })}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="ARS">ARS</option>
                      <option value="USD">USD</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  disabled={createUser.isPending}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
                >
                  {createUser.isPending ? 'Creando...' : 'Crear Usuario'}
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg transition-colors"
                >
                  Cancelar
                </button>
              </div>

              {createUser.isError && (
                <div className="mt-4 text-red-600">
                  Error: {(createUser.error as any)?.data?.detail || (createUser.error as Error).message}
                </div>
              )}
            </form>
          </div>
        )}

        {/* Users List */}
        {users && users.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {users.map((user) => (
              <div
                key={user.id}
                className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <UserIcon className="text-blue-600" size={24} />
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{user.name}</h3>
                    <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                      <Mail size={14} />
                      <span>{user.email}</span>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-gray-200">
                    <div className="flex items-center gap-2 text-gray-700">
                      <DollarSign size={16} className="text-green-600" />
                      <span className="font-semibold">
                        {user.wage_currency} {parseFloat(user.wage_amount).toLocaleString()}
                      </span>
                      <span className="text-sm text-gray-500">/ mes</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white p-12 rounded-lg shadow-md text-center">
            <UserIcon className="mx-auto text-gray-400 mb-4" size={48} />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No hay usuarios</h3>
            <p className="text-gray-600 mb-4">Creá el primer usuario para comenzar</p>
            <button
              onClick={() => setShowForm(true)}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              <Plus size={20} />
              Nuevo Usuario
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
