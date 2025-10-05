# 🎯 AD-3: Validación Avanzada de Respuestas

## User Story
**US-03**: Como usuario, quiero que el sistema valide mis respuestas (p. ej., formato de fecha), para evitar errores antes de continuar.

## Contexto
AD-2 implementó validación básica:
- ✅ Formato YYYY-MM-DD
- ✅ Longitud mínima 2 caracteres

AD-3 agrega **validaciones avanzadas y semánticas**:

## Criterios de Aceptación (Gherkin)

```gherkin
Scenario: Validación avanzada de fecha
  Given el usuario está respondiendo la pregunta de fecha
  When ingresa una fecha futura
  Then el sistema rechaza la respuesta
  And muestra un mensaje: "La fecha no puede estar en el futuro"

Scenario: Validación avanzada de fecha - rango razonable
  Given el usuario está respondiendo la pregunta de fecha
  When ingresa una fecha anterior a 10 años
  Then el sistema advierte pero permite continuar
  And muestra: "⚠️ Fecha muy antigua, ¿es correcto?"

Scenario: Validación de tipo de documento
  Given el usuario está respondiendo tipo de documento
  When ingresa texto con números o caracteres especiales
  Then el sistema rechaza la respuesta
  And muestra: "El tipo debe contener solo letras y espacios"

Scenario: Validación de nombre de cliente - caracteres permitidos
  Given el usuario está respondiendo nombre del cliente
  When ingresa texto con caracteres prohibidos (@, #, $, etc.)
  Then el sistema rechaza la respuesta
  And muestra: "El cliente solo puede contener letras, números, espacios, guiones y puntos"

Scenario: Sugerencias de corrección
  Given el usuario ingresa una respuesta inválida
  When el sistema detecta un error común
  Then muestra una sugerencia de corrección
  # Ejemplo: "15-01-2025" → "¿Quisiste decir 2025-01-15?"
```

## Invariantes del Producto

### Validaciones de Fecha
- ❌ **No futuro**: Fecha no puede ser mayor a hoy
- ⚠️ **Advertencia**: Si fecha > 10 años atrás (pero permite continuar)
- ✅ **Permitido**: Fechas entre hoy y 10 años atrás

### Validaciones de Tipo de Documento
- ✅ **Permitido**: Letras (a-z, A-Z), espacios, acentos
- ❌ **Rechazado**: Números, símbolos especiales
- **Min**: 2 caracteres
- **Max**: 50 caracteres
- **Ejemplos válidos**: "Factura", "Contrato de Servicios", "Nómina"
- **Ejemplos inválidos**: "Factura123", "Doc@2025", "F"

### Validaciones de Cliente
- ✅ **Permitido**: Letras, números, espacios, guiones (-), puntos (.), acentos
- ❌ **Rechazado**: @, #, $, %, &, *, (, ), etc.
- **Min**: 2 caracteres
- **Max**: 100 caracteres
- **Ejemplos válidos**: "Acme Corp.", "Cliente-123", "José Pérez"
- **Ejemplos inválidos**: "Cliente@Email.com", "Test#1", "X"

### Mensajes de Error Mejorados
En lugar de solo "mínimo 2 caracteres", mostrar:
- **Fecha**: "La fecha debe estar en formato YYYY-MM-DD y no puede ser futura. Ejemplo: 2025-01-15"
- **Tipo**: "El tipo debe contener solo letras (min 2, max 50). Ejemplo: Factura"
- **Cliente**: "El cliente puede contener letras, números, espacios, guiones y puntos (min 2, max 100). Ejemplo: Acme Corp."

## Endpoints Esperados (Backend)

Los endpoints existentes de AD-2 se mantienen, pero con validación mejorada:

```python
# POST /api/questions/answer
# Ahora valida con reglas más estrictas

# Body: { "question_id": "date", "answer": "2030-01-15", "file_id": "..." }
# Response 400: {
#   "detail": "La fecha no puede estar en el futuro",
#   "suggestion": null
# }

# Body: { "question_id": "doc_type", "answer": "Factura123", "file_id": "..." }
# Response 400: {
#   "detail": "El tipo debe contener solo letras y espacios",
#   "suggestion": "Factura"  # Sugerencia limpiada
# }
```

## Componente Frontend Esperado

El componente `QuestionFlow` se mejora para:
- Mostrar mensajes de error más descriptivos
- Mostrar sugerencias cuando estén disponibles
- Botón "Usar sugerencia" si hay sugerencia

## Archivos a Modificar/Crear

**Backend**:
- ✏️ `backend/app/validators.py` - Agregar validaciones avanzadas
- ✨ `backend/tests/test_validators_advanced.py` - Tests para validaciones avanzadas

**Frontend**:
- ✏️ `frontend/src/utils/validators.ts` - Agregar validaciones client-side avanzadas
- ✏️ `frontend/src/components/QuestionFlow.tsx` - Mostrar sugerencias
- ✨ `frontend/src/components/QuestionFlow.test.tsx` - Tests para sugerencias

**E2E**:
- ✨ `e2e/validation-advanced.spec.ts` - Tests E2E de validaciones avanzadas

## Lista de Pruebas Derivadas

| # | Descripción | Capa | Estado |
|---|------------|------|--------|
| 1 | Backend rechaza fecha futura | Backend | ❌ |
| 2 | Backend advierte fecha > 10 años pero permite | Backend | ❌ |
| 3 | Backend rechaza tipo con números | Backend | ❌ |
| 4 | Backend rechaza tipo con símbolos | Backend | ❌ |
| 5 | Backend rechaza tipo > 50 chars | Backend | ❌ |
| 6 | Backend rechaza cliente con símbolos prohibidos | Backend | ❌ |
| 7 | Backend rechaza cliente > 100 chars | Backend | ❌ |
| 8 | Backend genera sugerencia para tipo con números | Backend | ❌ |
| 9 | Backend genera sugerencia para fecha mal formateada | Backend | ❌ |
| 10 | Frontend valida fecha futura antes de enviar | Frontend | ❌ |
| 11 | Frontend muestra sugerencia cuando disponible | Frontend | ❌ |
| 12 | Frontend permite usar sugerencia con un click | Frontend | ❌ |
| 13 | E2E: Flujo con fecha futura rechazada | E2E | ❌ |
| 14 | E2E: Flujo con sugerencia aceptada | E2E | ❌ |

## Formato de Salida Requerido

Igual que AD-1 y AD-2:
1. Lista de pruebas (tabla) ✅
2. Tests RED (código completo)
3. Implementación GREEN (código mínimo)
4. Refactor
5. Cobertura
6. Árbol de archivos
7. Comandos
8. Commits con `feat(validation): ... (AD-3)`
9. PR description con DoD
10. Notas técnicas
