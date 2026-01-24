import React from 'react';
import { Outlet } from 'react-router-dom';
import { useSidebar } from '../../application/contexts/SidebarContext';
import { Sidebar } from '../components/Sidebar';
import { CurrencyToggle } from '../components/CurrencyToggle';
import { UserSelector } from '../components/UserSelector';
import { Menu } from 'lucide-react';

export const MainLayout: React.FC = () => {
  const { isCollapsed, toggleSidebar } = useSidebar();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow fixed top-0 left-0 right-0 z-30 h-16">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-md hover:bg-gray-100"
              aria-label="Toggle sidebar"
            >
              <Menu />
            </button>
            <div className="flex items-center gap-2">
              <span className="text-2xl">💰</span>
              <div className="text-lg font-bold">CashData</div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <CurrencyToggle />
            <UserSelector />
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <Sidebar />

      {/* Main content area */}
      <main className={`pt-20 transition-all duration-300 ${isCollapsed ? 'pl-20' : 'pl-72'}`}>
        <div className="max-w-7xl mx-auto px-4 py-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
