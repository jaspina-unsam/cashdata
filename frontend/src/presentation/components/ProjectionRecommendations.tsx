/**
 * Component: ProjectionRecommendations
 * 
 * Displays advantages and personalized recommendations based on projection results.
 */

interface ProjectionRecommendationsProps {
  recommendations: string[];
}

export function ProjectionRecommendations({ recommendations }: ProjectionRecommendationsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
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
        <h4 className="font-bold text-purple-900 mb-2">🎯 Recomendaciones personalizadas</h4>
        <ul className="text-sm text-slate-700 space-y-1">
          {recommendations.map((rec, idx) => (
            <li key={idx}>{rec}</li>
          ))}
        </ul>
      </div>
      
      <div className="md:col-span-2 p-4 bg-green-50 border-l-4 border-green-400 rounded">
        <h4 className="font-bold text-green-900 mb-2">🚀 Factor multiplicador: Tu carrera</h4>
        <p className="text-sm text-slate-700">
          Con tu perfil (datos + tech + remote), un aumento de 50-100% es completamente alcanzable en 2-3 años. 
          Si llegás a USD 4.000-5.000/mes, el proyecto lo completás en 3 años sin sacrificar calidad de vida. 
          <strong> Invertí en tu desarrollo profesional tanto como en el ahorro.</strong>
        </p>
      </div>
    </div>
  );
}
