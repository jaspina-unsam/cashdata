import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from './application';
import { CurrencyProvider } from './application/contexts/CurrencyContext';
import { UserProvider } from './application/contexts/UserContext';
import { SidebarProvider } from './application/contexts/SidebarContext';
import { MainLayout } from './presentation/layouts/MainLayout';
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

function HomePage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold">CashData</h1>
      <p className="mt-2 text-gray-600">Dashboard en construcción 🏗️</p>
    </div>
  );
}



export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <CurrencyProvider>
        <UserProvider>
          <SidebarProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<MainLayout />}>
                  <Route index element={<HomePage />} />
                  <Route path="users" element={<UsersPage />} />
                  <Route path="categories" element={<CategoriesPage />} />
                  <Route path="payment-methods" element={<PaymentMethodsPage />} />
                  <Route path="credit-cards" element={<CreditCardsPage />} />
                  <Route path="purchases" element={<PurchasesPage />} />
                  <Route path="purchases/:id/edit" element={<EditPurchasePage />} />
                  <Route path="statements" element={<StatementsPage />} />
                  <Route path="statements/:id" element={<StatementDetailPage />} />
                  <Route path="budgets" element={<BudgetsPage />} />
                  <Route path="budgets/:budgetId" element={<BudgetDetailPage />} />
                  <Route path="exchange-rates" element={<ExchangeRatesPage />} />
                  <Route path="projections" element={<ProjectionsPage />} />
                </Route>
              </Routes>
            </BrowserRouter>
          </SidebarProvider>
        </UserProvider>
      </CurrencyProvider>
      {/* <ReactQueryDevtools initialIsOpen={false} /> */}
    </QueryClientProvider>
  );
}