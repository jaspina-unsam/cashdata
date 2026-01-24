import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from './application';
import { CurrencyProvider } from './application/contexts/CurrencyContext';
import { 
  UsersPage, 
  CategoriesPage, 
  CreditCardsPage, 
  PurchasesPage, 
  EditPurchasePage,
  PaymentMethodsPage,
} from './presentation';
import { StatementsPage } from './presentation/pages/StatementsPage';
import { StatementDetailPage } from './presentation/pages/StatementDetailPage';
import { BudgetsPage } from './presentation/pages/BudgetsPage';
import { BudgetDetailPage } from './presentation/pages/BudgetDetailPage';
import { ExchangeRatesPage } from './presentation/pages/ExchangeRatesPage';
import { ProjectionsPage } from './presentation/pages/ProjectionsPage';
import { CurrencyToggle } from './presentation/components/CurrencyToggle';

function HomePage() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Link to="/users">
        <Card title="👥 Usuarios" subtitle="Gestioná usuarios" />
      </Link>
      <Link to="/categories">
        <Card title="🏷️ Categorías" subtitle="Organizá tus gastos" />
      </Link>
      <Link to="/payment-methods">
        <Card title="💳 Métodos de Pago" subtitle="Tarjetas, cuentas y billeteras" />
      </Link>
      <Link to="/credit-cards">
        <Card title="💳 Tarjetas" subtitle="Seguimiento de tarjetas" />
      </Link>
      <Link to="/purchases">
        <Card title="📊 Gastos" subtitle="Registrá tus gastos diarios" />
      </Link>
      <Link to="/statements">
        <Card title="📄 Resumenes" subtitle="Ver resumenes mensuales" />
      </Link>
      <Link to="/budgets">
        <Card title="💰 Presupuestos" subtitle="Gastos compartidos" />
      </Link>
      <Link to="/exchange-rates">
        <Card title="💱 Tipos de Cambio" subtitle="Cotizaciones USD/ARS" />
      </Link>
      <Link to="/projections">
        <Card title="📈 Proyecciones" subtitle="Planificá tu ahorro a 5 años" />
      </Link>
    </div>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-gradient-to-r from-blue-600 to-blue-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/">
              <h1 className="text-3xl font-bold text-white">💰 CashData</h1>
              <p className="text-blue-100 text-sm mt-1">Tus finanzas bajo control</p>
            </Link>
            <CurrencyToggle />
          </div>
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
    <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition-shadow border border-gray-100 cursor-pointer">
      <h2 className="text-2xl font-semibold mb-2">{title}</h2>
      <p className="text-gray-600">{subtitle}</p>
      <div className="mt-4 pt-4 border-t border-gray-100">
        <span className="text-sm text-blue-600 font-medium">Ver más →</span>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <CurrencyProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/users" element={<UsersPage />} />
              <Route path="/categories" element={<CategoriesPage />} />
              <Route path="/payment-methods" element={<PaymentMethodsPage />} />
              <Route path="/credit-cards" element={<CreditCardsPage />} />
              <Route path="/purchases" element={<PurchasesPage />} />
              <Route path="/purchases/:id/edit" element={<EditPurchasePage />} />
              <Route path="/statements" element={<StatementsPage />} />
              <Route path="/statements/:id" element={<StatementDetailPage />} />
              <Route path="/budgets" element={<BudgetsPage />} />
              <Route path="/budgets/:budgetId" element={<BudgetDetailPage />} />
              <Route path="/exchange-rates" element={<ExchangeRatesPage />} />
              <Route path="/projections" element={<ProjectionsPage />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </CurrencyProvider>
      {/* <ReactQueryDevtools initialIsOpen={false} /> */}
    </QueryClientProvider>
  );
}