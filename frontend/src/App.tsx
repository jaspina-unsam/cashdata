import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from './application';
import { CategoriesPage, CreditCardsPage } from './presentation';

function HomePage() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Link to="/categories">
        <Card title="🏷️ Categorías" subtitle="Organizá tus gastos" />
      </Link>
      <Link to="/credit-cards">
        <Card title="💳 Tarjetas" subtitle="Seguimiento de tarjetas" />
      </Link>
      <Card title="📊 Gastos" subtitle="Registrá tus gastos diarios" />
    </div>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-gradient-to-r from-blue-600 to-blue-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <Link to="/">
            <h1 className="text-3xl font-bold text-white">💰 CashData</h1>
            <p className="text-blue-100 text-sm mt-1">Tu finanzas bajo control</p>
          </Link>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
}

function Card({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition-shadow border border-gray-100">
      <h2 className="text-2xl font-semibold mb-2">{title}</h2>
      <p className="text-gray-600">{subtitle}</p>
      <div className="mt-4 pt-4 border-t border-gray-100">
        <span className="text-sm text-blue-600 font-medium">Próximamente →</span>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/categories" element={<CategoriesPage />} />
            <Route path="/credit-cards" element={<CreditCardsPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
      {/* <ReactQueryDevtools initialIsOpen={false} /> */}
    </QueryClientProvider>
  );
}