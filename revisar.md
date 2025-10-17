📋 Propuesta de Implementación: Integración Dolphin + Gemini

  🔍 Análisis de Dolphin

  Capacidades de Dolphin:
  - ✅ Parseo de documentos PDF/imágenes completos
  - ✅ Extracción de texto, tablas, fórmulas y figuras
  - ✅ Análisis de layout con orden de lectura natural
  - ✅ Salida en formato JSON + Markdown
  - ✅ Soporte para PDFs multi-página
  - ✅ Procesamiento paralelo eficiente (batch)

  Modelo ligero: Solo 0.3B de parámetros

  ---
  🏗️ Arquitectura Propuesta

  Nuevo Flujo con Paso de Previsualización

  1. Usuario sube documento (POST /api/upload-temp)
     ↓
  2. ✨ NUEVO: Parseo con Dolphin (POST /api/document/preview)
     ↓
  3. ✨ NUEVO: Resumen con Gemini
     ↓
  4. ✨ NUEVO: Mostrar previsualización al usuario
     ↓
  5. Usuario confirma documento (POST /api/document/confirm)
     ↓
  6. Flujo normal de preguntas URSALL
     ↓
  7. Generación de path y subida a Dropbox

  ---
  📁 Estructura de Archivos a Crear

  backend/app/
  ├── dolphin_parser.py        # Wrapper para integrar Dolphin
  ├── document_preview.py       # Lógica de previsualización
  └── gemini_summarizer.py      # Resumen con Gemini

  backend/Dolphin/              # Ya existe, solo usar
  └── [archivos de Dolphin]

---
  🔄 Flujo Completo Propuesto

  ┌─────────────────────┐
  │  1. Upload File     │
  │  POST /upload-temp  │
  └──────────┬──────────┘
             │
             ↓
  ┌─────────────────────┐
  │  2. Generate Preview│
  │  POST /preview      │ → Dolphin parsea → Gemini resume
  └──────────┬──────────┘
             │
             ↓
  ┌─────────────────────┐
  │  3. Show Preview    │
  │  Frontend muestra   │ → Usuario ve resumen + confianza
  │  resumen y pregunta │
  └──────────┬──────────┘
             │
          ┌──┴──┐
          │ ¿OK?│
          └──┬──┘
       SI ↓    ↓ NO
     ┌────────┐  └──→ Cancelar + Limpiar
     │ Confirm│
     └───┬────┘
         │
         ↓
  ┌──────────────────────┐
  │ 4. Start Questions   │ → Flujo URSALL normal
  │ POST /questions/start│
  └──────────────────────┘

  ---
  📊 Ventajas de Esta Implementación

  ✅ Experiencia de Usuario

  1. Validación temprana: Usuario ve si el documento es correcto ANTES de las preguntas
  2. Contexto visual: Resumen ayuda a confirmar que subió el archivo correcto
  3. Confianza: Score de confianza indica si el análisis es fiable
  4. Ahorro de tiempo: Evita completar 11 preguntas para luego darse cuenta del error

  ✅ Técnico

  1. Modularidad: Cada componente (Dolphin, Gemini, Preview) es independiente
  2. Reusabilidad: DolphinParser se puede usar en otros contextos
  3. Fallback: Si Dolphin falla, el flujo normal continúa
  4. Caché: El parseo se puede cachear para no repetir

  ✅ Legal (URSALL)

  1. Extracción inteligente: Gemini puede pre-identificar partes, jurisdicción, etc.
  2. Sugerencias: Puede sugerir valores para las preguntas
  3. Validación: Detecta si NO es un documento legal