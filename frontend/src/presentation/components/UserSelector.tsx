import React from 'react';
import { useActiveUser } from '../../application/contexts/UserContext';

export function UserSelector() {
  const { activeUserId, users, setActiveUserId, isLoading } = useActiveUser();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = parseInt(e.target.value, 10);
    setActiveUserId(id);
  };

  if (isLoading) {
    return (
      <select disabled className="px-3 py-1 border rounded-md bg-gray-50 text-gray-500 cursor-not-allowed">
        <option>Cargando usuarios...</option>
      </select>
    );
  }

  if (!users || users.length === 0) {
    return (
      <select disabled className="px-3 py-1 border rounded-md bg-gray-50 text-gray-500 cursor-not-allowed">
        <option>Sin usuarios</option>
      </select>
    );
  }

  return (
    <select
      value={activeUserId}
      onChange={handleChange}
      className="px-3 py-1 border border-gray-300 rounded-md bg-white text-gray-700 hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer transition-colors"
      aria-label="Selector de usuario"
    >
      {users.map((u) => (
        <option key={u.id} value={u.id}>
          {u.name}
        </option>
      ))}
    </select>
  );
}
