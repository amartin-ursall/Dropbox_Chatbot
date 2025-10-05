# 🎯 AD-4: Renombrado Automático y Sugerencia de Ruta en Dropbox

## User Stories
**US-04**: Como usuario, quiero que el sistema proponga un nuevo nombre de archivo basado en mis respuestas y conserve la extensión original, para estandarizar la nomenclatura.

**US-05**: Como usuario, quiero que el sistema me sugiera la ruta de Dropbox donde debería ir el archivo según mis respuestas, para ubicarlo correctamente.

## Contexto
AD-3 completó el flujo de preguntas con validación avanzada:
- ✅ Usuario sube archivo
- ✅ Responde 3 preguntas: doc_type, client, date
- ✅ Validación avanzada con sugerencias
- ✅ Genera nombre: `{date}_{type}_{client}.{ext}`

AD-4 agrega:
- **Sugerencia de ruta en Dropbox** basada en tipo de documento
- **Preview completo** antes de confirmar (nombre + ruta)

## Criterios de Aceptación (Gherkin)

```gherkin
Scenario: Sugerencia de ruta basada en tipo de documento
  Given el usuario completó las preguntas
  And el tipo de documento es "Factura"
  When el sistema genera la sugerencia de ruta
  Then la ruta sugerida es "/Documentos/Facturas"

Scenario: Sugerencia de ruta para Contratos
  Given el usuario completó las preguntas
  And el tipo de documento es "Contrato"
  When el sistema genera la sugerencia de ruta
  Then la ruta sugerida es "/Documentos/Contratos"

Scenario: Sugerencia de ruta para Recibos
  Given el usuario completó las preguntas
  And el tipo de documento es "Recibo"
  When el sistema genera la sugerencia de ruta
  Then la ruta sugerida es "/Documentos/Recibos"

Scenario: Ruta por defecto para tipos no mapeados
  Given el usuario completó las preguntas
  And el tipo de documento es "Reporte Mensual"
  When el sistema genera la sugerencia de ruta
  Then la ruta sugerida es "/Documentos/Otros"

Scenario: Preview completo antes de confirmar
  Given el usuario completó las preguntas
  When el sistema genera el preview
  Then muestra el nombre sugerido "{fecha}_{tipo}_{cliente}.{ext}"
  And muestra la ruta sugerida en Dropbox
  And muestra botones "Confirmar" y "Cancelar"

Scenario: Usuario confirma subida
  Given el preview está visible
  When el usuario hace click en "Confirmar"
  Then el sistema prepara la subida a Dropbox
  And muestra mensaje "Preparando subida..."
  # Nota: La subida real a Dropbox será AD-5

Scenario: Usuario cancela subida
  Given el preview está visible
  When el usuario hace click en "Cancelar"
  Then el sistema cancela el flujo
  And muestra mensaje "Operación cancelada"
  And permite subir un nuevo archivo
```

## Invariantes del Producto

### Mapeo de Tipos a Rutas
| Tipo de Documento | Ruta Dropbox |
|------------------|--------------|
| Factura, Facturas | `/Documentos/Facturas` |
| Contrato, Contratos | `/Documentos/Contratos` |
| Recibo, Recibos | `/Documentos/Recibos` |
| Nómina, Nóminas, Nomina | `/Documentos/Nóminas` |
| Presupuesto, Presupuestos | `/Documentos/Presupuestos` |
| *Otros casos* | `/Documentos/Otros` |

**Reglas**:
- Case-insensitive (ej: "factura", "FACTURA", "Factura" → `/Documentos/Facturas`)
- Plural/singular: ambos mapean a la misma ruta
- Acentos: maneja "Nómina" y "Nomina"

### Formato de Preview
```
📄 Nombre sugerido:
   2025-01-15_Factura_Acme-Corp.pdf

📁 Ruta en Dropbox:
   /Documentos/Facturas

[Confirmar]  [Cancelar]
```

## Endpoints Esperados (Backend)

### Nuevo endpoint: Sugerencia de ruta
```python
POST /api/suggest-path
Body: {
  "doc_type": "Factura",
  "client": "Acme Corp",
  "date": "2025-01-15"
}

Response 200: {
  "suggested_path": "/Documentos/Facturas",
  "suggested_name": "2025-01-15_Factura_Acme-Corp.pdf",
  "full_path": "/Documentos/Facturas/2025-01-15_Factura_Acme-Corp.pdf"
}
```

### Modificación de endpoint existente
```python
POST /api/questions/generate-name
# Ya existe desde AD-2, ahora también devuelve ruta

Body: {
  "file_id": "abc123",
  "answers": {
    "doc_type": "Factura",
    "client": "Acme Corp",
    "date": "2025-01-15"
  },
  "original_extension": ".pdf"
}

Response 200: {
  "suggested_name": "2025-01-15_Factura_Acme-Corp.pdf",
  "original_extension": ".pdf",
  "suggested_path": "/Documentos/Facturas",  # NUEVO
  "full_path": "/Documentos/Facturas/2025-01-15_Factura_Acme-Corp.pdf"  # NUEVO
}
```

## Componente Frontend Esperado

### Nuevo componente: UploadPreview
```tsx
interface UploadPreviewProps {
  suggestedName: string
  suggestedPath: string
  onConfirm: () => void
  onCancel: () => void
}

// Muestra preview con nombre + ruta
// Botones de confirmar/cancelar
```

### Modificación de QuestionFlow
```tsx
// Al completar preguntas, obtiene nombre Y ruta
// Muestra UploadPreview en lugar de solo el nombre
```

## Archivos a Modificar/Crear

**Backend**:
- ✨ `backend/app/path_mapper.py` - Lógica de mapeo tipo → ruta
- ✨ `backend/tests/test_path_mapper.py` - Tests de mapeo
- ✏️ `backend/app/main.py` - Agregar endpoint `/api/suggest-path`
- ✏️ `backend/app/main.py` - Modificar `/api/questions/generate-name` para incluir ruta

**Frontend**:
- ✨ `frontend/src/components/UploadPreview.tsx` - Componente de preview
- ✨ `frontend/src/components/UploadPreview.test.tsx` - Tests
- ✏️ `frontend/src/components/QuestionFlow.tsx` - Integrar preview
- ✏️ `frontend/src/App.tsx` - Manejar estados de confirmación/cancelación

**E2E**:
- ✨ `e2e/upload-preview.spec.ts` - Tests E2E de preview y confirmación

## Lista de Pruebas Derivadas

| # | Descripción | Capa | Estado |
|---|------------|------|--------|
| 1 | Backend mapea "Factura" a "/Documentos/Facturas" | Backend | ❌ |
| 2 | Backend mapea "factura" (lowercase) correctamente | Backend | ❌ |
| 3 | Backend mapea "Contrato" a "/Documentos/Contratos" | Backend | ❌ |
| 4 | Backend mapea "Recibo" a "/Documentos/Recibos" | Backend | ❌ |
| 5 | Backend mapea "Nómina" a "/Documentos/Nóminas" | Backend | ❌ |
| 6 | Backend mapea "Nomina" (sin acento) a "/Documentos/Nóminas" | Backend | ❌ |
| 7 | Backend mapea tipo no conocido a "/Documentos/Otros" | Backend | ❌ |
| 8 | Backend genera full_path correctamente | Backend | ❌ |
| 9 | Endpoint /suggest-path devuelve ruta correcta | Backend | ❌ |
| 10 | Endpoint /generate-name incluye suggested_path | Backend | ❌ |
| 11 | Frontend muestra preview con nombre y ruta | Frontend | ❌ |
| 12 | Frontend muestra botones Confirmar y Cancelar | Frontend | ❌ |
| 13 | Frontend llama onConfirm al hacer click | Frontend | ❌ |
| 14 | Frontend llama onCancel al hacer click | Frontend | ❌ |
| 15 | E2E: Flujo completo muestra preview correcto | E2E | ❌ |
| 16 | E2E: Click en Confirmar prepara subida | E2E | ❌ |
| 17 | E2E: Click en Cancelar reinicia flujo | E2E | ❌ |

## Formato de Salida Requerido

Siguiendo metodología TDD estricta:

### 1️⃣ Fase RED
- Lista de pruebas en tabla ✅
- Tests backend (`test_path_mapper.py`)
- Tests frontend (`UploadPreview.test.tsx`)
- Tests E2E (`upload-preview.spec.ts`)
- **Todos los tests deben fallar**

### 2️⃣ Fase GREEN
- Implementar `path_mapper.py` (mapeo básico)
- Modificar `/api/questions/generate-name`
- Crear componente `UploadPreview.tsx`
- Modificar `QuestionFlow.tsx` para usar preview
- **Todos los tests deben pasar**

### 3️⃣ Fase REFACTOR
- Extraer constantes de rutas a config
- Mejorar estructura de mapeo
- Optimizar renders en React

### 4️⃣ Documentación
- Cobertura de tests
- Árbol de archivos modificados
- Comandos para ejecutar
- PR description con DoD

### 5️⃣ Commits
```
feat(path): add path mapper for document types (AD-4)
feat(api): add suggest-path endpoint (AD-4)
feat(ui): add upload preview component (AD-4)
test(e2e): add preview confirmation tests (AD-4)
```

## Notas Técnicas

### Path Mapper
```python
# backend/app/path_mapper.py
PATH_MAP = {
    "factura": "/Documentos/Facturas",
    "facturas": "/Documentos/Facturas",
    "contrato": "/Documentos/Contratos",
    # ...
}

def suggest_path(doc_type: str) -> str:
    normalized = normalize_doc_type(doc_type)
    return PATH_MAP.get(normalized, "/Documentos/Otros")
```

### Preview Component
```tsx
// Muestra card con:
// - Icono de archivo
// - Nombre sugerido (bold)
// - Ruta sugerida (con icono de carpeta)
// - Botones con estados loading
```

### Estado de Confirmación
```tsx
// App.tsx maneja:
// - 'idle': Esperando upload
// - 'questions': Respondiendo preguntas
// - 'preview': Mostrando preview
// - 'confirmed': Usuario confirmó (AD-5 subirá)
// - 'cancelled': Usuario canceló
```

## Definition of Done (DoD)

- [ ] ✅ 17 tests passing (6 backend, 6 frontend, 5 E2E)
- [ ] ✅ Cobertura > 80% en archivos nuevos
- [ ] ✅ Preview funcional con nombre + ruta
- [ ] ✅ Mapeo case-insensitive funciona
- [ ] ✅ Botones Confirmar/Cancelar funcionan
- [ ] ✅ Ruta "/Documentos/Otros" para tipos desconocidos
- [ ] ✅ Sin regresiones en AD-1, AD-2, AD-3
- [ ] ✅ Commits con mensaje "(AD-4)"
- [ ] ✅ PR description completo
