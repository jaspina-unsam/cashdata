import React from 'react';
import { NavLink } from 'react-router-dom';
import { useSidebar } from '../../application/contexts/SidebarContext';
import { Home, Users, Tag, Wallet, CreditCard, ShoppingCart, FileText, DollarSign, Repeat, BarChart2 } from 'lucide-react';

const navItems = [
  { to: '/', icon: <Home size={18} />, label: 'Inicio' },
  { to: '/users', icon: <Users size={18} />, label: 'Usuarios' },
  { to: '/categories', icon: <Tag size={18} />, label: 'Categorías' },
  { to: '/payment-methods', icon: <Wallet size={18} />, label: 'Métodos de Pago' },
  { to: '/credit-cards', icon: <CreditCard size={18} />, label: 'Tarjetas' },
  { to: '/purchases', icon: <ShoppingCart size={18} />, label: 'Gastos' },
  { to: '/statements', icon: <FileText size={18} />, label: 'Resúmenes' },
  { to: '/budgets', icon: <DollarSign size={18} />, label: 'Presupuestos' },
  { to: '/exchange-rates', icon: <Repeat size={18} />, label: 'Tipos de Cambio' },
  { to: '/projections', icon: <BarChart2 size={18} />, label: 'Proyecciones' },
];

export const Sidebar: React.FC = () => {
  const { isCollapsed } = useSidebar();

  return (
    <aside
      className={`fixed left-0 top-16 h-[calc(100vh-4rem)] bg-white shadow-lg transition-all duration-300 z-20 ${isCollapsed ? 'w-16' : 'w-64'}`}
    >
      <nav className="flex flex-col p-2 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md hover:bg-gray-100 transition-colors ${
                isActive ? 'bg-blue-50 font-semibold text-blue-700' : 'text-gray-700'
              }`
            }
          >
            <div className="flex items-center justify-center w-6">{item.icon}</div>
            {!isCollapsed && <span className="truncate">{item.label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};
