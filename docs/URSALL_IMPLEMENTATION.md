# Implementación Sistema URSALL Legal

## Resumen

Se ha implementado un sistema completo para gestionar la subida de archivos a Dropbox siguiendo la estructura organizacional de URSALL Legal, basada en la especificación en `context/ursall/carpetas.md`.

## Arquitectura

### Módulos Creados

#### 1. `backend/app/path_mapper_ursall.py`
**Propósito**: Generar rutas de Dropbox según la estructura URSALL Legal

**Funciones principales:**
- `build_procedimiento_name()`: Construye el nombre del procedimiento judicial
  - Formato: `AAAA_MM_Juzgado_Demarcación_NºProcedimiento/AAAA_ParteA Vs ParteB_Materia`
  - Ejemplo: `2025_08_SC2_Tenerife_455/2025_Pedro Perez Vs Cabildo Gomera_Despidos`

- `build_proyecto_name()`: Construye el nombre del proyecto jurídico
  - Formato: `AAAA_MM_Cliente_Proyecto_Materia`
  - Ejemplo: `2025_06_AyuntamientoAdeje_Informe_SeguroSalud`

- `suggest_path_ursall()`: Genera la ruta completa incluyendo subcarpetas
  - Retorna: path completo, subfolder específica, estructura de carpetas a crear

**Mapeos incluidos:**
- `JURISDICTION_MAP`: Abreviaturas de jurisdicciones (CA, SC, CIV, PEN, JPI)
- `DOC_TYPE_TO_PROCEDIMIENTO_FOLDER`: Mapeo de tipos de documento a subcarpetas de procedimiento
- `DOC_TYPE_TO_PROYECTO_FOLDER`: Mapeo de tipos de documento a subcarpetas de proyecto

#### 2. `backend/app/nlp_extractor_legal.py`
**Propósito**: Extraer información legal de las respuestas del usuario usando NLP

**Extractores implementados:**
- `extract_jurisdiccion()`: Identifica el tipo de juzgado
- `extract_juzgado_numero()`: Extrae el número del juzgado
- `extract_demarcacion()`: Extrae la demarcación geográfica
- `extract_num_procedimiento()`: Extrae número de procedimiento (formato XXX/YYYY)
- `extract_partes()`: Extrae las partes del procedimiento (actor vs demandado)
- `extract_materia()`: Extrae la materia del procedimiento
- `extract_proyecto_info()`: Extrae información de proyectos (nombre y materia)

**Patrones regex incluidos:**
- Jurisdicciones: contencioso, social, civil, penal, instrucción
- Números de procedimiento: 455/2025, 123/2024, etc.
- Partes: "Pedro Perez vs Cabildo Gomera", "Actor: X, Demandado: Y"
- Materias: Despidos, Fijeza, Urbanismo, Art316CP, etc.

#### 3. `backend/app/questions_ursall.py`
**Propósito**: Gestionar el flujo de preguntas para URSALL

**Flujos implementados:**

**Procedimiento Judicial (11 preguntas):**
1. tipo_trabajo → "procedimiento"
2. client → Nombre del cliente
3. jurisdiccion → Tipo de juzgado
4. juzgado_num → Número del juzgado
5. demarcacion → Demarcación
6. num_procedimiento → XXX/YYYY
7. fecha_procedimiento → YYYY-MM-DD
8. parte_a → Parte actora
9. parte_b → Parte demandada
10. materia_proc → Materia
11. doc_type_proc → Tipo de documento

**Proyecto Jurídico (7 preguntas):**
1. tipo_trabajo → "proyecto"
2. client → Nombre del cliente
3. proyecto_year → YYYY
4. proyecto_month → MM
5. proyecto_nombre → Nombre del proyecto
6. proyecto_materia → Materia del proyecto
7. doc_type_proyecto → Tipo de documento

**Funciones principales:**
- `get_first_question_ursall()`: Retorna primera pregunta
- `get_next_question_ursall()`: Retorna siguiente pregunta basada en respuestas previas
- `is_last_question_ursall()`: Verifica si es la última pregunta
- `validate_ursall_answers()`: Valida que todas las respuestas necesarias estén presentes

#### 4. `backend/app/main_ursall.py`
**Propósito**: Endpoints API para el flujo URSALL

**Endpoints implementados:**

**POST `/api/ursall/questions/start`**
- Inicia el flujo de preguntas URSALL
- Retorna la primera pregunta (tipo_trabajo)

**POST `/api/ursall/questions/answer`**
- Procesa respuestas del usuario
- Extrae información usando NLP legal
- Valida respuestas
- Retorna siguiente pregunta o indica finalización

**POST `/api/ursall/generate-path`**
- Genera ruta completa de Dropbox
- Genera nombre de archivo
- Retorna estructura de carpetas a crear

**POST `/api/ursall/upload-final`**
- Crea toda la estructura de carpetas en Dropbox
- Sube el archivo a la ubicación correcta
- Limpia archivos temporales

## Integración

El sistema URSALL se ha integrado en el `main.py` principal:

```python
from app.main_ursall import router as ursall_router
app.include_router(ursall_router)
```

Esto expone todos los endpoints URSALL bajo el prefijo `/api/ursall/`.

## Estructura de Carpetas Generada

### Procedimiento Judicial
```
/CLIENTE/
└── 1. Procedimientos Judiciales/
    └── AAAA_MM_Juzgado_Demarcación_NºProcedimiento/AAAA_ParteA Vs ParteB_Materia/
        ├── 01. Escritos presentados/
        ├── 02. Resoluciones judiciales/
        ├── 03. Pruebas/
        │   ├── 03.1 Testifical/
        │   ├── 03.2 Pericial/
        │   └── 03.3 Documental/
        ├── 04. Doctrina y jurisprudencia/
        ├── 05. Notificaciones del Juzgado/
        ├── 06. Anotaciones internas/
        ├── 07. Documentación del cliente/
        ├── 08. Carpeta 0 – Almacenamiento rápido/
        ├── 09. Agenda procesal y plazos/
        └── 10. Costas y gastos/
```

### Proyecto Jurídico
```
/CLIENTE/
└── 2. Proyectos Jurídicos/
    └── AAAA_MM_Cliente_Proyecto_Materia/
        ├── 00. General/
        ├── 01. Documentación recibida/
        ├── 02. Borradores/
        ├── 03. Documentación de estudio/
        ├── 04. Comunicaciones/
        ├── 05. Informe/Documento final/
        ├── 06. Contratos o convenios asociados/
        └── 07. Anexos y notas adicionales/
```

## Características Implementadas

### 1. Extracción Inteligente
El sistema utiliza NLP para entender respuestas naturales:
- "Juzgado Social número 2 de Tenerife" → extrae jurisdicción, número, demarcación
- "Pedro Perez vs Cabildo Gomera" → extrae ambas partes
- "Artículo 316 CP" → formatea como "Art316CP"

### 2. Validaciones
- Formato de fechas: YYYY-MM-DD
- Formato de procedimiento: XXX/YYYY
- Jurisdicciones válidas
- Campos requeridos según tipo de trabajo

### 3. Mapeo Automático de Documentos
El sistema mapea automáticamente el tipo de documento a la subcarpeta correcta:

**Procedimientos:**
- Sentencia → `02. Resoluciones judiciales`
- Escrito → `01. Escritos presentados`
- Pericial → `03.2 Pericial`
- etc.

**Proyectos:**
- Informe → `05. Informe/Documento final`
- Contrato → `06. Contratos o convenios asociados`
- Borrador → `02. Borradores`
- etc.

### 4. Creación Automática de Estructura
El sistema crea automáticamente:
- Carpeta del cliente
- Tipo de trabajo (Procedimientos/Proyectos)
- Carpeta específica del caso
- Todas las subcarpetas estándar

## Uso en Frontend

### 1. Iniciar Flujo URSALL
```javascript
const response = await fetch('/api/ursall/questions/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ file_id: uploadedFileId })
});
const firstQuestion = await response.json();
```

### 2. Responder Preguntas
```javascript
const response = await fetch('/api/ursall/questions/answer', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_id: uploadedFileId,
    question_id: currentQuestionId,
    answer: userAnswer
  })
});
const result = await response.json();
// result.next_question contiene la siguiente pregunta
// result.completed indica si terminó el flujo
```

### 3. Generar Ruta
```javascript
const response = await fetch('/api/ursall/generate-path', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_id: uploadedFileId,
    answers: allAnswers,
    original_extension: '.pdf'
  })
});
const pathInfo = await response.json();
// pathInfo.suggested_path contiene la ruta completa
// pathInfo.folder_structure contiene las carpetas a crear
```

### 4. Subir Archivo
```javascript
const response = await fetch('/api/ursall/upload-final', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_id: uploadedFileId,
    filename: pathInfo.suggested_name,
    dropbox_path: pathInfo.suggested_path,
    folder_structure: pathInfo.folder_structure
  })
});
const result = await response.json();
```

## Testing

### Test Procedimiento Judicial

```bash
# 1. Iniciar
curl -X POST http://localhost:8000/api/ursall/questions/start \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test-proc"}'

# 2. Responder tipo_trabajo
curl -X POST http://localhost:8000/api/ursall/questions/answer \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test-proc", "question_id": "tipo_trabajo", "answer": "procedimiento"}'

# 3. Cliente
curl -X POST http://localhost:8000/api/ursall/questions/answer \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test-proc", "question_id": "client", "answer": "GRUPO GORETTI"}'

# 4. Jurisdicción
curl -X POST http://localhost:8000/api/ursall/questions/answer \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test-proc", "question_id": "jurisdiccion", "answer": "social"}'

# ... continuar con el resto de preguntas
```

### Test Proyecto Jurídico

```bash
# 1. Iniciar
curl -X POST http://localhost:8000/api/ursall/questions/start \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test-proy"}'

# 2. Responder tipo_trabajo
curl -X POST http://localhost:8000/api/ursall/questions/answer \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test-proy", "question_id": "tipo_trabajo", "answer": "proyecto"}'

# ... continuar con el resto de preguntas
```

## Archivos Modificados/Creados

### Creados
- ✅ `backend/app/path_mapper_ursall.py` - Lógica de rutas URSALL
- ✅ `backend/app/nlp_extractor_legal.py` - Extracción NLP legal
- ✅ `backend/app/questions_ursall.py` - Flujo de preguntas URSALL
- ✅ `backend/app/main_ursall.py` - Endpoints API URSALL
- ✅ `docs/URSALL_USAGE.md` - Guía de uso
- ✅ `docs/URSALL_IMPLEMENTATION.md` - Documentación técnica

### Modificados
- ✅ `backend/app/main.py` - Integración del router URSALL

## Próximos Pasos (Recomendaciones)

### Frontend
1. Crear componente `QuestionFlowURSALL.tsx` similar al existente
2. Agregar switch para elegir entre flujo normal y URSALL
3. Adaptar UI para mostrar preguntas específicas de URSALL

### Mejoras
1. Implementar cache de estructuras de Dropbox para validación
2. Agregar sugerencias automáticas basadas en casos anteriores
3. Implementar búsqueda de procedimientos/proyectos existentes
4. Agregar validación de duplicados

### Testing
1. Crear tests unitarios para extractores NLP
2. Tests de integración para flujo completo
3. Tests E2E con Playwright para flujo URSALL

## Ventajas del Sistema

1. **Automatización completa**: Todo el proceso de creación de estructura está automatizado
2. **Extracción inteligente**: NLP extrae información de respuestas naturales
3. **Validaciones robustas**: Formatos y campos requeridos validados
4. **Mapeo automático**: Documentos se organizan automáticamente en subcarpetas correctas
5. **Escalable**: Fácil agregar nuevos tipos de documentos o jurisdicciones
6. **Mantenible**: Código modular y bien documentado
7. **Compatible**: Se integra perfectamente con el sistema existente

## Conclusión

El sistema URSALL Legal está completamente implementado y listo para usar. Permite organizar documentos legales siguiendo la estructura específica de URSALL, con extracción inteligente de información y creación automática de toda la estructura de carpetas necesaria en Dropbox.
