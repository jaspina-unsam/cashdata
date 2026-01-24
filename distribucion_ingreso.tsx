import React, { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Area, AreaChart } from 'recharts';

const DistribucionIngreso = () => {
  const [ingresoInicial] = useState(5000);
  const [gastosFijos, setGastosFijos] = useState(900);
  const [gastosVariables, setGastosVariables] = useState(400);
  const [fondoEmergencia, setFondoEmergencia] = useState(100);
  
  // Escenarios de desarrollo profesional
  const [escenarioProfesional, setEscenarioProfesional] = useState('moderado');
  
  // Escenarios económicos
  const [inflacionConstruccion, setInflacionConstruccion] = useState(8);
  const [devaluacionAnual, setDevaluacionAnual] = useState(0);

  const escenarios = {
    conservador: { aumentoAnual: 0, nombre: 'Sin aumento' },
    moderado: { aumentoAnual: 10, nombre: 'Moderado (+10%/año)' },
    optimista: { aumentoAnual: 15, nombre: 'Optimista (+15%/año)' },
    muyOptimista: { aumentoAnual: 25, nombre: 'Muy optimista (+25%/año)' }
  };

  const distribucionActual = useMemo(() => {
    const ahorroObjetivo = ingresoInicial - gastosFijos - gastosVariables - fondoEmergencia;
    
    return {
      gastosFijos,
      gastosVariables,
      ahorroObjetivo: Math.max(0, ahorroObjetivo),
      fondoEmergencia,
      total: gastosFijos + gastosVariables + fondoEmergencia + Math.max(0, ahorroObjetivo),
      porcentajes: {
        gastosFijos: ((gastosFijos / ingresoInicial) * 100).toFixed(1),
        gastosVariables: ((gastosVariables / ingresoInicial) * 100).toFixed(1),
        ahorroObjetivo: ((Math.max(0, ahorroObjetivo) / ingresoInicial) * 100).toFixed(1),
        fondoEmergencia: ((fondoEmergencia / ingresoInicial) * 100).toFixed(1)
      }
    };
  }, [gastosFijos, gastosVariables, fondoEmergencia, ingresoInicial]);

  const proyeccion5Años = useMemo(() => {
    const meses = 60;
    let datos = [];
    let acumuladoAhorro = 0;
    let acumuladoEmergencia = 0;
    const aumentoMensual = escenarios[escenarioProfesional].aumentoAnual / 100 / 12;
    const rendimiento = 0.07;
    const rendimientoMensual = Math.pow(1 + rendimiento, 1/12) - 1;
    
    // Efecto devaluación en gastos
    const reduccionGastosMensual = devaluacionAnual / 100 / 12;
    
    // Costo de construcción
    const costoInicial = 75000;
    const inflacionMensual = Math.pow(1 + inflacionConstruccion / 100, 1/12) - 1;
    
    let ingresoActual = ingresoInicial;
    let gastosActuales = gastosFijos + gastosVariables;
    
    for (let mes = 1; mes <= meses; mes++) {
      // Aumentos salariales progresivos
      if (mes > 1) {
        ingresoActual *= (1 + aumentoMensual);
      }
      
      // Reducción de gastos por devaluación
      if (mes > 1 && devaluacionAnual > 0) {
        gastosActuales *= (1 - reduccionGastosMensual);
      }
      
      // Calcular ahorro del mes
      const ahorroMes = Math.max(0, ingresoActual - gastosActuales - fondoEmergencia);
      
      // Aguinaldo (junio y diciembre)
      const esAguinaldo = mes % 6 === 0;
      const montoAguinaldo = esAguinaldo ? (ingresoActual * 0.5) : 0;
      
      // Acumular con intereses
      acumuladoAhorro = (acumuladoAhorro + ahorroMes + montoAguinaldo) * (1 + rendimientoMensual);
      
      // Fondo de emergencia (sin rendimiento, en cuenta aparte)
      if (acumuladoEmergencia < 10000) {
        acumuladoEmergencia += fondoEmergencia;
      }
      
      // Costo de construcción actual
      const costoConstruccion = costoInicial * Math.pow(1 + inflacionMensual, mes);
      
      const fecha = new Date(2026, 0, 1);
      fecha.setMonth(fecha.getMonth() + mes - 1);
      
      datos.push({
        mes,
        fecha: `${fecha.toLocaleString('es-AR', { month: 'short', year: '2-digit' })}`,
        año: fecha.getFullYear(),
        ingreso: Math.round(ingresoActual),
        ahorroMensual: Math.round(ahorroMes),
        acumuladoAhorro: Math.round(acumuladoAhorro),
        acumuladoEmergencia: Math.round(Math.min(acumuladoEmergencia, 10000)),
        costoConstruccion: Math.round(costoConstruccion),
        diferencia: Math.round(acumuladoAhorro - costoConstruccion),
        aguinaldo: esAguinaldo ? Math.round(montoAguinaldo) : 0
      });
    }
    
    return datos;
  }, [escenarioProfesional, gastosFijos, gastosVariables, fondoEmergencia, inflacionConstruccion, devaluacionAnual, ingresoInicial]);

  const ultimoDato = proyeccion5Años[proyeccion5Años.length - 1];
  const alcanza = ultimoDato.acumuladoAhorro >= ultimoDato.costoConstruccion;

  const resumenAnual = useMemo(() => {
    const años = [2026, 2027, 2028, 2029, 2030];
    return años.map(año => {
      const datosAño = proyeccion5Años.filter(d => d.año === año);
      const ultimoMes = datosAño[datosAño.length - 1];
      const primerMes = datosAño[0];
      const aguinaldosAño = datosAño.reduce((sum, d) => sum + d.aguinaldo, 0);
      
      return {
        año,
        ingresoPromedio: Math.round((ultimoMes.ingreso + primerMes.ingreso) / 2),
        ahorrado: Math.round(ultimoMes.acumuladoAhorro - (primerMes.acumuladoAhorro || 0)),
        aguinaldos: Math.round(aguinaldosAño),
        acumuladoTotal: ultimoMes.acumuladoAhorro
      };
    });
  }, [proyeccion5Años]);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">
          Plan de Ahorro Personalizado 2026-2030
        </h1>
        <div className="text-slate-600 mb-6">
          <p className="text-sm">✅ Sin alquiler | ✅ Trabajo remoto | ✅ Base salarial dolarizada</p>
          <p className="text-lg font-semibold mt-2">
            Ingreso actual: <span className="text-blue-600">{formatCurrency(ingresoInicial)}</span>/mes
          </p>
        </div>

        {/* Controles principales */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-slate-800">💰 Distribución mensual actual</h3>
            
            <div className="bg-red-50 p-4 rounded-lg border border-red-200">
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-slate-700">
                  🏠 Gastos Fijos (sin alquiler)
                </label>
                <span className="text-lg font-bold text-red-600">
                  {formatCurrency(gastosFijos)} ({distribucionActual.porcentajes.gastosFijos}%)
                </span>
              </div>
              <input
                type="range"
                min="500"
                max="1400"
                step="50"
                value={gastosFijos}
                onChange={(e) => setGastosFijos(Number(e.target.value))}
                className="w-full"
              />
              <div className="text-xs text-slate-600 mt-2">
                Expensas, servicios, comida, seguros, etc.
              </div>
            </div>

            <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-slate-700">
                  🛍️ Gastos Variables
                </label>
                <span className="text-lg font-bold text-orange-600">
                  {formatCurrency(gastosVariables)} ({distribucionActual.porcentajes.gastosVariables}%)
                </span>
              </div>
              <input
                type="range"
                min="200"
                max="800"
                step="50"
                value={gastosVariables}
                onChange={(e) => setGastosVariables(Number(e.target.value))}
                className="w-full"
              />
              <div className="text-xs text-slate-600 mt-2">
                Entretenimiento, salidas, compras, etc.
              </div>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-slate-700">
                  🛡️ Fondo de Emergencia (mensual)
                </label>
                <span className="text-lg font-bold text-blue-600">
                  {formatCurrency(fondoEmergencia)} ({distribucionActual.porcentajes.fondoEmergencia}%)
                </span>
              </div>
              <input
                type="range"
                min="50"
                max="300"
                step="25"
                value={fondoEmergencia}
                onChange={(e) => setFondoEmergencia(Number(e.target.value))}
                className="w-full"
              />
              <div className="text-xs text-slate-600 mt-2">
                Objetivo: llegar a USD 10.000 de colchón
              </div>
            </div>

            <div className="bg-green-50 p-4 rounded-lg border-2 border-green-300">
              <div className="flex justify-between items-center">
                <label className="text-sm font-semibold text-slate-700">
                  🏗️ Ahorro para Construcción
                </label>
                <span className="text-2xl font-bold text-green-600">
                  {formatCurrency(distribucionActual.ahorroObjetivo)} ({distribucionActual.porcentajes.ahorroObjetivo}%)
                </span>
              </div>
              <div className="text-xs text-green-700 mt-2 font-semibold">
                ⭐ Lo que queda después de gastos
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-bold text-slate-800">🚀 Escenarios de desarrollo</h3>
            
            <div className="bg-purple-50 p-4 rounded-lg border-2 border-purple-300">
              <label className="text-sm font-semibold text-slate-700 mb-2 block">
                📈 Proyección de carrera
              </label>
              <select
                value={escenarioProfesional}
                onChange={(e) => setEscenarioProfesional(e.target.value)}
                className="w-full p-2 rounded border border-purple-300 font-semibold"
              >
                {Object.entries(escenarios).map(([key, val]) => (
                  <option key={key} value={key}>{val.nombre}</option>
                ))}
              </select>
              <div className="text-xs text-slate-600 mt-2">
                Impacto en tu sueldo durante los próximos 5 años
              </div>
            </div>

            <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-slate-700">
                  📉 Inflación construcción (% anual)
                </label>
                <span className="text-lg font-bold text-orange-600">
                  {inflacionConstruccion}%
                </span>
              </div>
              <input
                type="range"
                min="3"
                max="15"
                step="0.5"
                value={inflacionConstruccion}
                onChange={(e) => setInflacionConstruccion(Number(e.target.value))}
                className="w-full"
              />
              <div className="text-xs text-slate-600 mt-2">
                Cómo sube el costo del m² en dólares
              </div>
            </div>

            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-slate-700">
                  💵 Devaluación del peso (% anual)
                </label>
                <span className="text-lg font-bold text-green-600">
                  {devaluacionAnual}%
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="40"
                step="5"
                value={devaluacionAnual}
                onChange={(e) => setDevaluacionAnual(Number(e.target.value))}
                className="w-full"
              />
              <div className="text-xs text-slate-600 mt-2">
                Reduce tus gastos en pesos expresados en USD
              </div>
            </div>
          </div>
        </div>

        {/* Resultado principal */}
        <div className={`p-6 rounded-xl mb-6 ${alcanza ? 'bg-green-50 border-2 border-green-300' : 'bg-yellow-50 border-2 border-yellow-300'}`}>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm font-semibold text-slate-600 mb-1">Total acumulado (dic 2030)</div>
              <div className="text-2xl font-bold text-green-700">{formatCurrency(ultimoDato.acumuladoAhorro)}</div>
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-600 mb-1">Costo proyectado obra</div>
              <div className="text-2xl font-bold text-orange-700">{formatCurrency(ultimoDato.costoConstruccion)}</div>
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-600 mb-1">
                {alcanza ? '✅ Excedente' : '⚡ Diferencia'}
              </div>
              <div className={`text-2xl font-bold ${alcanza ? 'text-green-700' : 'text-yellow-700'}`}>
                {formatCurrency(Math.abs(ultimoDato.diferencia))}
              </div>
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-600 mb-1">Fondo emergencia</div>
              <div className="text-2xl font-bold text-blue-700">{formatCurrency(ultimoDato.acumuladoEmergencia)}</div>
            </div>
          </div>
          <div className="mt-4 text-sm text-slate-700">
            {alcanza ? (
              <span className="font-semibold">🎉 ¡Excelente! Llegarías al objetivo con margen de seguridad.</span>
            ) : (
              <span className="font-semibold">💪 Muy cerca del objetivo. Considerá hacer el proyecto en 2 etapas o aumentá ingresos.</span>
            )}
          </div>
        </div>

        {/* Gráfico de evolución */}
        <div className="bg-white rounded-lg mb-6">
          <h3 className="text-lg font-bold text-slate-800 mb-4">📊 Evolución del plan (60 meses)</h3>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={proyeccion5Años}>
              <defs>
                <linearGradient id="colorAhorro" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="fecha" 
                tick={{ fontSize: 11 }}
                interval={5}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip 
                formatter={(value) => formatCurrency(value)}
                labelStyle={{ color: '#334155' }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="acumuladoAhorro"
                stroke="#10b981"
                fillOpacity={1}
                fill="url(#colorAhorro)"
                name="Ahorro acumulado"
              />
              <Line 
                type="monotone" 
                dataKey="costoConstruccion" 
                stroke="#f97316" 
                strokeWidth={3}
                strokeDasharray="5 5"
                name="Costo de la obra"
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey="ingreso" 
                stroke="#8b5cf6" 
                strokeWidth={2}
                name="Ingreso mensual"
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Resumen anual */}
        <div className="bg-white rounded-lg mb-6">
          <h3 className="text-lg font-bold text-slate-800 mb-4">📅 Resumen año por año</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-100">
                <tr>
                  <th className="p-3 text-left">Año</th>
                  <th className="p-3 text-right">Ingreso promedio</th>
                  <th className="p-3 text-right">Ahorrado en el año</th>
                  <th className="p-3 text-right">Aguinaldos</th>
                  <th className="p-3 text-right">Total acumulado</th>
                </tr>
              </thead>
              <tbody>
                {resumenAnual.map((año, i) => (
                  <tr key={año.año} className={i % 2 === 0 ? 'bg-slate-50' : ''}>
                    <td className="p-3 font-bold">{año.año}</td>
                    <td className="p-3 text-right">{formatCurrency(año.ingresoPromedio)}</td>
                    <td className="p-3 text-right text-green-600 font-semibold">{formatCurrency(año.ahorrado)}</td>
                    <td className="p-3 text-right text-emerald-600">{formatCurrency(año.aguinaldos)}</td>
                    <td className="p-3 text-right font-bold text-blue-600">{formatCurrency(año.acumuladoTotal)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Consejos personalizados */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-bold text-blue-900 mb-2">💡 Ventajas de tu situación</h4>
            <ul className="text-sm text-slate-700 space-y-1">
              <li>✅ Sin alquiler: ahorrás USD 400-600/mes</li>
              <li>✅ Trabajo remoto: sin gastos de transporte</li>
              <li>✅ Base dolarizada: protección contra inflación</li>
              <li>✅ Casa propia: podés hacer obra sin mudarte</li>
              <li>✅ Joven en tech: alto potencial de crecimiento</li>
            </ul>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <h4 className="font-bold text-purple-900 mb-2">🎯 Recomendaciones clave</h4>
            <ul className="text-sm text-slate-700 space-y-1">
              <li>🎓 Priorizá terminar la licenciatura (game changer)</li>
              <li>💼 Buscá posiciones en empresas internacionales</li>
              <li>📈 Considerá freelance en paralelo (Upwork, Toptal)</li>
              <li>🏗️ Planeá obra en etapas si es necesario</li>
              <li>💰 Destiná aguinaldos 100% a construcción</li>
            </ul>
          </div>
        </div>

        <div className="mt-6 p-4 bg-green-50 border-l-4 border-green-400 rounded">
          <h4 className="font-bold text-green-900 mb-2">🚀 Factor multiplicador: Tu carrera</h4>
          <p className="text-sm text-slate-700">
            Con tu perfil (datos + tech + remote), un aumento de 50-100% es completamente alcanzable en 2-3 años. 
            Si llegás a USD 4.000-5.000/mes, el proyecto lo completás en 3 años sin sacrificar calidad de vida. 
            <strong> Invertí en tu desarrollo profesional tanto como en el ahorro.</strong>
          </p>
        </div>
      </div>
    </div>
  );
};

export default DistribucionIngreso;