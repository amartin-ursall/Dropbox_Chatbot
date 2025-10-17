# Flujo Completo: Dolphin + Gemini + Frontend

## ✅ Implementación Verificada

### Backend - Flujo de Datos

```
📄 Archivo Upload
    ↓
🔵 POST /api/upload-temp
    ↓ (guarda archivo temporal)
    ↓
🟣 POST /api/document/preview
    ↓
📊 document_preview.py
    ↓
    ├─→ dolphin_parser.py
    │   └─→ 🐬 Dolphin.parse_document(file_path)
    │       └─→ Retorna: {text, elements, pages, has_tables, has_figures}
    │
    └─→ gemini_summarizer.py
        └─→ 🤖 summarize_document(text, metadata, "legal")
            └─→ Retorna: {
                  summary, document_type, confidence,
                  is_legal_document, key_information,
                  suggested_answers
                }
    ↓
🎯 Retorna preview completo al frontend
```

### Frontend - Flujo de Usuario

```
1. Usuario sube archivo
   └─→ QuestionFlow llama /api/upload-temp

2. ✨ NUEVO: Se muestra el documento VISUALMENTE
   └─→ QuestionFlow.useEffect() → setShowDocumentViewer(true)
       └─→ Muestra DocumentViewer component
           ├─→ PDF: Se muestra en iframe usando /api/file-preview/{file_id}
           ├─→ Imagen: Se muestra en <img> usando /api/file-preview/{file_id}
           └─→ Otros: Placeholder con icono y nombre

   Usuario puede:
   ├─→ ✅ Confirmar y Analizar → Continúa al paso 3
   └─→ ❌ Cancelar → Elimina archivo y permite nuevo upload

3. Usuario confirmó → Se procesa con Dolphin + Gemini
   └─→ handleViewerConfirm() llama generatePreview()
       └─→ POST /api/document/preview
       └─→ Muestra loading "🔍 Analizando Documento"

4. Muestra DocumentPreview component (Análisis AI)
   ├─→ Resumen del documento
   ├─→ Tipo de documento (demanda, contrato, etc.)
   ├─→ Confianza del análisis (Alta/Media/Baja)
   ├─→ Información clave detectada
   │   ├─→ Partes
   │   ├─→ Jurisdicción
   │   ├─→ Juzgado
   │   ├─→ Número procedimiento
   │   └─→ Materia
   └─→ Respuestas sugeridas para pre-llenar

5. Usuario confirma análisis o cancela
   ├─→ ✅ Confirmar → POST /api/document/confirm (confirmed: true)
   │   └─→ Inicia flujo de preguntas URSALL
   └─→ ❌ Cancelar → POST /api/document/confirm (confirmed: false)
       └─→ Limpia archivo temporal y permite nuevo upload
```

## 🔍 Verificación del Flujo

### 1. Archivo llega correctamente a Dolphin ✅

**Ruta del archivo:**
- Upload → `TEMP_STORAGE_PATH/{file_id}_{filename}`
- Preview endpoint encuentra archivo: `TEMP_STORAGE_PATH.glob(f"{file_id}_*")`
- Se pasa a Dolphin: `dolphin_parser.parse_document(str(temp_file))`

**Código (backend/app/main.py:279-295):**
```python
temp_file = None
for file in TEMP_STORAGE_PATH.glob(f"{file_id}_*"):
    temp_file = file
    break

preview_result = await generate_document_preview(
    file_path=str(temp_file),  # ✅ Archivo pasa a Dolphin
    file_id=file_id,
    target_use=target_use
)
```

### 2. Dolphin parsea y pasa texto a Gemini ✅

**Código (backend/app/document_preview.py:95-116):**
```python
# Paso 1: Dolphin parsea
parsed_content, parse_confidence = self.dolphin_parser.parse_document(file_path)

# Extraer metadata
metadata = {
    "pages": parsed_content.get("pages", 1),
    "has_tables": parsed_content.get("has_tables", False),
    "has_figures": parsed_content.get("has_figures", False)
}

document_text = parsed_content.get("text", "")  # ✅ Texto extraído

# Paso 2: Gemini resume
summary_result = await summarize_document(
    document_text,  # ✅ Texto pasa a Gemini
    metadata,
    target_use
)
```

### 3. Gemini procesa y retorna resumen ✅

**Código (backend/app/gemini_summarizer.py:31-77):**
```python
# Construye prompt según tipo (legal/general)
if target_use == "legal":
    prompt = _build_legal_summary_prompt(document_text, metadata)

# Llama a Gemini API
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
response = await client.post(url, json=payload)

# Parse respuesta JSON
parsed_result = _parse_gemini_summary_response(result_text)

# Retorna: ✅
# {
#   "summary": "...",
#   "document_type": "demanda",
#   "is_legal_document": true,
#   "confidence": 0.92,
#   "key_information": {...},
#   "suggested_answers": {...}
# }
```

### 4. Preview se muestra en Frontend ✅

**Código (frontend/src/components/QuestionFlow.tsx:502-512):**
```typescript
// Si hay preview, muestra DocumentPreview
if (showPreview && previewData && fileMetadata) {
  return (
    <DocumentPreview
      preview={previewData}  // ✅ Datos de Dolphin + Gemini
      fileName={fileMetadata.original_name}
      onConfirm={handleDocumentConfirm}
      onCancel={handleDocumentCancel}
      isLoading={isLoading}
    />
  )
}
```

**El componente DocumentPreview muestra:**
- ✅ Resumen (línea 59): `{preview.summary}`
- ✅ Tipo de documento (línea 65): `{preview.document_type}`
- ✅ Confianza (línea 70): `{preview.confidence}`
- ✅ Información clave (línea 95-145): partes, jurisdicción, juzgado, etc.
- ✅ Respuestas sugeridas (línea 153-171)

## 📋 Componentes Creados

### Backend
1. ✅ `backend/app/dolphin_parser.py` - Wrapper para Dolphin
2. ✅ `backend/app/gemini_summarizer.py` - Resumidor con Gemini
3. ✅ `backend/app/document_preview.py` - Orquestador Dolphin + Gemini

### Frontend
1. ✅ `frontend/src/components/DocumentPreview.tsx` - UI del preview
2. ✅ `frontend/src/components/DocumentPreview.css` - Estilos
3. ✅ `frontend/src/components/QuestionFlow.tsx` - Modificado para integrar preview

### Endpoints API
1. ✅ `POST /api/document/preview` - Generar preview
2. ✅ `POST /api/document/confirm` - Confirmar/rechazar documento
3. ✅ `GET /api/document/preview/status` - Estado del servicio

## 🧪 Testing Manual

### Paso 1: Verificar que Dolphin está configurado
```bash
cd scripts
.\status-background.ps1
```

**Salida esperada:**
```
Configuración de Servicios:
  Dolphin Preview:  HABILITADO
    Estado: Operacional
  Gemini AI:        HABILITADO
```

### Paso 2: Iniciar servicios
```bash
.\start-background.ps1
```

### Paso 3: Probar endpoint de preview
```bash
# 1. Upload archivo
curl -X POST http://localhost:8000/api/upload-temp \
  -F "file=@documento_legal.pdf"

# Copiar file_id de la respuesta

# 2. Generar preview
curl -X POST http://localhost:8000/api/document/preview \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "uuid-aqui",
    "target_use": "legal"
  }'
```

**Respuesta esperada:**
```json
{
  "file_id": "uuid",
  "status": "success",
  "preview": {
    "summary": "Demanda de despido presentada ante el Juzgado Social...",
    "document_type": "demanda",
    "confidence": 0.92,
    "is_legal_document": true,
    "pages": 5,
    "has_tables": true,
    "has_figures": false,
    "suggested_workflow": "ursall",
    "key_information": {
      "partes": ["Juan Pérez", "Empresa XYZ S.L."],
      "jurisdiccion": "Social",
      "juzgado": "Juzgado Social 2 de Tenerife",
      "numero_procedimiento": "455/2025"
    },
    "suggested_answers": {
      "client": "Juan Pérez",
      "partes": "Juan Pérez vs Empresa XYZ S.L.",
      "jurisdiccion": "Social"
    }
  },
  "raw_text": "Primera parte del texto...",
  "error": null
}
```

### Paso 4: Probar en el Frontend

1. Abrir http://localhost:5173
2. Subir un documento PDF legal
3. Esperar mensaje "🔍 Analizando Documento"
4. Ver preview con:
   - Resumen del documento
   - Tipo identificado
   - Confianza del análisis
   - Información clave extraída
   - Botones "Confirmar" y "Cancelar"
5. Click "Confirmar" → Inicia flujo de preguntas URSALL
6. Click "Cancelar" → Vuelve a upload

## 🔧 Solución de Problemas

### Error: "Dolphin parser not available"

**Causa:** Modelo Dolphin no descargado o mal configurado

**Solución:**
1. Descargar modelo (300MB):
   - Google Drive: https://drive.google.com/drive/folders/1PQJ3UutepXvunizZEw-uGaQ0BCzf-mie
   - Baidu Yun: https://pan.baidu.com/s/15zcARoX0CTOHKbW8bFZovQ?pwd=9rpx

2. Colocar archivos en:
   ```
   backend/Dolphin/checkpoints/
   ├── dolphin_model.bin
   └── dolphin_tokenizer.json
   ```

3. Reiniciar backend

### Error: "Document parsing failed"

**Causa:** Archivo no compatible o corrupto

**Solución:**
- Verificar que el archivo es PDF, JPG o PNG
- Verificar que el archivo no está corrupto
- Revisar logs en `logs/backend_*.log`

### Preview no muestra información clave

**Causa:** Gemini no pudo extraer información o documento no es legal

**Solución:**
- Verificar que GEMINI_API_KEY está configurado
- El documento puede ser no-legal (flujo estándar se usará)
- Ver confianza (si < 0.6, el análisis es poco confiable)

### Frontend no muestra preview

**Causa:** Error en la llamada API o estado no actualizado

**Solución:**
1. Abrir DevTools → Console
2. Verificar errores de red
3. Verificar que `/api/document/preview` responde 200
4. Verificar estado de QuestionFlow:
   ```javascript
   console.log('showPreview:', showPreview)
   console.log('previewData:', previewData)
   ```

## 📊 Logs de Depuración

### Backend logs importantes

```python
# document_preview.py
logger.info(f"Starting document preview for file: {file_path}")
logger.info(f"Preview generated successfully for {file_id}: {preview['document_type']}")

# dolphin_parser.py
logger.info(f"Parsing image: {image_path}")
logger.info(f"Parsing PDF: {pdf_path}")

# gemini_summarizer.py
logger.info(f"Document summarized successfully: {parsed_result.get('document_type')}")
```

### Frontend logs importantes

```javascript
// QuestionFlow.tsx
console.log('Generating preview for file:', fileId)
console.log('Preview result:', result)
console.warn('Preview failed, continuing with normal flow:', error)
```

## ✨ Características Implementadas

### Preview Inteligente
- ✅ Parseo automático con Dolphin
- ✅ Resumen con Gemini
- ✅ Extracción de información legal
- ✅ Sugerencias de respuestas
- ✅ Indicador de confianza

### UI/UX
- ✅ Loading state con mensaje descriptivo
- ✅ Preview card con información estructurada
- ✅ Badges visuales (tablas, figuras, documento legal)
- ✅ Botones de confirmar/cancelar
- ✅ Animaciones suaves

### Fallbacks
- ✅ Si Dolphin falla → continúa con flujo normal
- ✅ Si Gemini falla → muestra preview básico
- ✅ Si preview falla → inicia preguntas directamente

## 🎯 Próximos Pasos (Opcionales)

1. **Pre-llenado de respuestas**: Usar `suggested_answers` para auto-completar preguntas
2. **Caché de previews**: Guardar previews en localStorage o backend
3. **Preview mejorado**: Mostrar extractos del texto con highlighting
4. **Validación cruzada**: Comparar respuestas del usuario con preview
5. **Thumbnails**: Generar imágenes de vista previa del documento

## 📚 Referencias

- Dolphin docs: `docs/DOLPHIN_INTEGRATION.md`
- URSALL docs: `docs/URSALL_IMPLEMENTATION.md`
- Actualizaciones: `ACTUALIZACIONES.md`

---

## Resumen Ejecutivo

✅ **Flujo Completo Implementado:**

1. Usuario sube archivo → Dolphin lo parsea automáticamente
2. Texto parseado → Se pasa a Gemini para resumir
3. Resumen + información clave → Se muestra en el frontend
4. Usuario confirma → Continúa con preguntas URSALL (con datos pre-extraídos)
5. Usuario cancela → Limpia todo y permite nuevo upload

**Estado:** 100% funcional con fallbacks robustos ✅
