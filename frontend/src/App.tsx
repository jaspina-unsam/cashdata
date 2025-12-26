import { BrowserRouter, Routes, Route } from 'react-router-dom';

function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-gradient-to-r from-blue-600 to-blue-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-white">💰 CashData</h1>
          <p className="text-blue-100 text-sm mt-1">Tu finanzas bajo control</p>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card title="💳 Gastos" subtitle="Registrá tus gastos diarios" />
          <Card title="📊 Ciclos" subtitle="Seguimiento de tarjetas" />
          <Card title="🎯 Planificación" subtitle="Metas de ahorro" />
        </div>
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
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />} />
      </Routes>
    </BrowserRouter>
  );
}