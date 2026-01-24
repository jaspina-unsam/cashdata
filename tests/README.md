# End-to-End Tests con Playwright

Este directorio contiene tests e2e para verificar funcionalidades críticas de CashData.

## Tests Disponibles

### 1. Delete Purchase (`delete-purchase.spec.ts`)
Verifica que las compras se puedan eliminar correctamente, incluyendo:
- Eliminación de compras normales
- Eliminación de compras con budget expenses asociados (debería eliminar primero los budget_expenses de installments y de la compra)

### 2. Reassign Statement (`reassign-statement.spec.ts`)
Verifica que las compras de pago único puedan reasignarse a diferentes statements:
- Reasignación de cuota única a otro statement
- Verifica que el dropdown muestre solo statements de la tarjeta correcta
- Verifica que no haya errores 422 al guardar

## Cómo Ejecutar

### Ejecutar todos los tests
```bash
npm run test:e2e
```

### Ejecutar tests específicos
```bash
# Solo test de eliminación
npm run test:delete

# Solo test de reasignación
npm run test:reassign
```

### Modo UI (interactivo)
```bash
npm run test:e2e:ui
```

### Modo debug
```bash
npm run test:e2e:debug
```

### Ver tests en modo headed (con browser visible)
```bash
npm run test:e2e:headed
```

## Configuración

Los tests están configurados para ejecutarse contra:
- **Base URL**: `http://cumulonimbus.local`

Para cambiar la URL, edita `playwright.config.ts`:
```typescript
use: {
  baseURL: 'http://tu-servidor.local',
}
```

## Requisitos

- El servidor debe estar corriendo en `http://cumulonimbus.local`
- Debe haber datos de prueba disponibles:
  - Al menos una compra existente para el test de eliminación
  - Al menos una compra de pago único (1 cuota) con una tarjeta de crédito para el test de reasignación
  - Al menos 2 statements para la misma tarjeta para poder reasignar

## Resolución de Problemas

### Tests fallan con timeout
- Verifica que el servidor esté corriendo
- Aumenta el timeout en `playwright.config.ts`

### No encuentra elementos
- Los tests usan selectores flexibles que intentan múltiples estrategias
- Verifica que los elementos tengan los textos esperados en español
- Considera agregar `data-testid` attributes en el código para selectores más confiables

### Statements no aparecen en el dropdown
- Verifica que la credit_card tenga statements creados en la base de datos
- El test verificará que el `payment_method_id` se convierta correctamente al `credit_card_id`
