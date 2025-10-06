# Guía de Uso - Sistema URSALL Legal

## Descripción General

El sistema URSALL Legal implementa la estructura organizacional específica para documentos legales de URSALL Legal, siguiendo la estructura documentada en `context/ursall/carpetas.md`.

## Estructura de Carpetas

### Nivel 0: Cliente
Cada cliente tiene una carpeta raíz:
- **Formato Grupo**: `GRUPO + NOMBRE` (ej: GRUPO GORETTI, GRUPO NEUMATICOS)
- **Formato Individual/Empresa**: Nombre completo (ej: JJ. TEALQUILA Y GESTIONA SL)

### Nivel 1: Tipo de Trabajo
Cada cliente contiene dos subcarpetas principales:
1. **Procedimientos Judiciales**
2. **Proyectos Jurídicos**

---

## 1. Procedimientos Judiciales

### Nomenclatura
Formato: `AAAA_MM_Juzgado_Demarcación_NºProcedimiento/AAAA_ParteA Vs ParteB_Materia`

**Ejemplo:**
```
2025_08_SC2_Tenerife_455/2025_Pedro Perez Vs Cabildo Gomera_Despidos
```

### Abreviaturas de Jurisdicción
| Jurisdicción | Abreviatura |
|--------------|-------------|
| Contencioso-Administrativo | CA |
| Social/Laboral | SC |
| Civil | CIV |
| Penal | PEN |
| Instrucción | JPI |

### Subcarpetas del Procedimiento
Cada procedimiento contiene automáticamente:
- `01. Escritos presentados`
- `02. Resoluciones judiciales`
- `03. Pruebas`
  - `03.1 Testifical`
  - `03.2 Pericial`
  - `03.3 Documental`
- `04. Doctrina y jurisprudencia`
- `05. Notificaciones del Juzgado`
- `06. Anotaciones internas`
- `07. Documentación del cliente`
- `08. Carpeta 0 – Almacenamiento rápido`
- `09. Agenda procesal y plazos`
- `10. Costas y gastos`

### Mapeo de Documentos a Subcarpetas
El sistema mapea automáticamente el tipo de documento a la subcarpeta correcta:

| Tipo de Documento | Subcarpeta |
|-------------------|------------|
| Escrito, Demanda, Contestación | 01. Escritos presentados |
| Sentencia, Auto, Resolución | 02. Resoluciones judiciales |
| Testifical, Testimonio | 03.1 Testifical |
| Pericial, Informe Pericial | 03.2 Pericial |
| Documental, Prueba Documental | 03.3 Documental |
| Jurisprudencia, Doctrina | 04. Doctrina y jurisprudencia |
| Notificación, Cédula | 05. Notificaciones del Juzgado |
| Nota, Anotación | 06. Anotaciones internas |
| Costas, Gastos | 10. Costas y gastos |
| *Otros* | 08. Carpeta 0 – Almacenamiento rápido |

---

## 2. Proyectos Jurídicos

### Nomenclatura
Formato: `AAAA_MM_Cliente_Proyecto_Materia`

**Ejemplo:**
```
2025_06_AyuntamientoAdeje_Informe_SeguroSalud
```

### Subcarpetas del Proyecto
Cada proyecto contiene automáticamente:
- `00. General`
- `01. Documentación recibida`
- `02. Borradores`
- `03. Documentación de estudio`
- `04. Comunicaciones`
- `05. Informe/Documento final`
- `06. Contratos o convenios asociados`
- `07. Anexos y notas adicionales`

### Mapeo de Documentos a Subcarpetas
| Tipo de Documento | Subcarpeta |
|-------------------|------------|
| Informe, Dictamen, Documento Final | 05. Informe/Documento final |
| Contrato, Convenio | 06. Contratos o convenios asociados |
| Borrador, Draft | 02. Borradores |
| Comunicación, Email, Correo | 04. Comunicaciones |
| Documentación, Recibido | 01. Documentación recibida |
| *Otros* | 00. General |

---

## API Endpoints

### Iniciar Flujo de Preguntas URSALL
```http
POST /api/ursall/questions/start
Content-Type: application/json

{
  "file_id": "uuid-del-archivo"
}
```

**Respuesta:**
```json
{
  "question_id": "tipo_trabajo",
  "question_text": "¿Es un Procedimiento Judicial o un Proyecto Jurídico?",
  "required": true
}
```

### Responder Pregunta
```http
POST /api/ursall/questions/answer
Content-Type: application/json

{
  "file_id": "uuid-del-archivo",
  "question_id": "tipo_trabajo",
  "answer": "procedimiento"
}
```

**Respuesta:**
```json
{
  "next_question": {
    "question_id": "client",
    "question_text": "¿Cuál es el nombre del cliente?",
    "required": true
  },
  "completed": false,
  "extracted_value": "procedimiento"
}
```

### Generar Ruta y Nombre
```http
POST /api/ursall/generate-path
Content-Type: application/json

{
  "file_id": "uuid-del-archivo",
  "answers": { /* todas las respuestas */ },
  "original_extension": ".pdf"
}
```

**Respuesta:**
```json
{
  "suggested_name": "2025-08-15_Sentencia.pdf",
  "suggested_path": "/GRUPO GORETTI/1. Procedimientos Judiciales/2025_08_SC2_Tenerife_455_2025_Pedro Perez Vs Cabildo Gomera_Despidos/02. Resoluciones judiciales",
  "full_path": "/GRUPO GORETTI/1. Procedimientos Judiciales/.../02. Resoluciones judiciales/2025-08-15_Sentencia.pdf",
  "folder_structure": [
    "/GRUPO GORETTI",
    "/GRUPO GORETTI/1. Procedimientos Judiciales",
    "/GRUPO GORETTI/1. Procedimientos Judiciales/2025_08_SC2_Tenerife_455_2025_Pedro Perez Vs Cabildo Gomera_Despidos",
    "..."
  ],
  "tipo": "procedimiento",
  "subfolder": "02. Resoluciones judiciales"
}
```

---

## Flujo de Preguntas

### Procedimiento Judicial
1. **tipo_trabajo**: "procedimiento"
2. **client**: Nombre del cliente
3. **jurisdiccion**: Tipo de juzgado (contencioso/social/civil/penal/instrucción)
4. **juzgado_num**: Número del juzgado
5. **demarcacion**: Demarcación (Santa Cruz, Tenerife, etc.)
6. **num_procedimiento**: Número procedimiento (formato: 455/2025)
7. **fecha_procedimiento**: Fecha (formato: YYYY-MM-DD)
8. **parte_a**: Parte actora/demandante
9. **parte_b**: Parte demandada
10. **materia_proc**: Materia (Despidos, Fijeza, etc.)
11. **doc_type_proc**: Tipo de documento

### Proyecto Jurídico
1. **tipo_trabajo**: "proyecto"
2. **client**: Nombre del cliente
3. **proyecto_year**: Año (YYYY)
4. **proyecto_month**: Mes (MM)
5. **proyecto_nombre**: Nombre del proyecto
6. **proyecto_materia**: Materia del proyecto
7. **doc_type_proyecto**: Tipo de documento

---

## Extracción Inteligente (NLP)

El sistema utiliza NLP para extraer información automáticamente:

### Jurisdicción
- Input: "Juzgado de lo Social nº 2"
- Extrae: `jurisdiccion="social"`, `juzgado_num="2"`

### Partes
- Input: "Pedro Perez vs Cabildo Gomera"
- Extrae: `parte_a="Pedro Perez"`, `parte_b="Cabildo Gomera"`

### Materia
- Input: "Artículo 316 CP"
- Extrae: `materia="Art316CP"`

### Número de Procedimiento
- Input: "Procedimiento 455/2025"
- Extrae: `num_procedimiento="455/2025"`

---

## Ejemplo Completo: Procedimiento Judicial

**Datos de Entrada:**
```json
{
  "client": "GRUPO GORETTI",
  "tipo_trabajo": "procedimiento",
  "jurisdiccion": "social",
  "juzgado_num": "2",
  "demarcacion": "Tenerife",
  "num_procedimiento": "455/2025",
  "fecha_procedimiento": "2025-08-15",
  "parte_a": "Pedro Perez",
  "parte_b": "Cabildo Gomera",
  "materia_proc": "Despidos",
  "doc_type_proc": "Sentencia"
}
```

**Ruta Generada:**
```
/GRUPO GORETTI/1. Procedimientos Judiciales/2025_08_SC2_Tenerife_455/2025_Pedro Perez Vs Cabildo Gomera_Despidos/02. Resoluciones judiciales/2025-08-15_Sentencia.pdf
```

**Estructura Creada:**
- `/GRUPO GORETTI/`
- `/GRUPO GORETTI/1. Procedimientos Judiciales/`
- `/GRUPO GORETTI/1. Procedimientos Judiciales/2025_08_SC2_Tenerife_455/2025_Pedro Perez Vs Cabildo Gomera_Despidos/`
- Y todas las 10 subcarpetas del procedimiento

---

## Ejemplo Completo: Proyecto Jurídico

**Datos de Entrada:**
```json
{
  "client": "Ayuntamiento Adeje",
  "tipo_trabajo": "proyecto",
  "proyecto_year": "2025",
  "proyecto_month": "06",
  "proyecto_nombre": "Informe",
  "proyecto_materia": "Seguro Salud",
  "doc_type_proyecto": "Informe"
}
```

**Ruta Generada:**
```
/Ayuntamiento Adeje/2. Proyectos Jurídicos/2025_06_Ayuntamiento Adeje_Informe_SeguroSalud/05. Informe/Documento final/2025_06_Informe.pdf
```

**Estructura Creada:**
- `/Ayuntamiento Adeje/`
- `/Ayuntamiento Adeje/2. Proyectos Jurídicos/`
- `/Ayuntamiento Adeje/2. Proyectos Jurídicos/2025_06_Ayuntamiento Adeje_Informe_SeguroSalud/`
- Y todas las 8 subcarpetas del proyecto

---

## Notas Técnicas

### Sanitización de Nombres
- Los nombres se sanitizan automáticamente para ser válidos en Dropbox
- Se reemplazan caracteres especiales y se normalizan espacios
- Se mantienen acentos y caracteres especiales del español

### Creación de Carpetas
- El sistema crea automáticamente toda la estructura de carpetas necesaria
- Si una carpeta ya existe, no se sobrescribe
- Se crean recursivamente todas las subcarpetas estándar

### Validaciones
- Formatos de fecha: YYYY-MM-DD
- Número de procedimiento: XXX/YYYY
- Jurisdicciones válidas: contencioso, social, civil, penal, instrucción
- Tipo de trabajo: procedimiento o proyecto

---

## Testing

Para probar los endpoints URSALL:

```bash
# Iniciar servidor
uvicorn app.main:app --reload

# Test procedimiento judicial
curl -X POST http://localhost:8000/api/ursall/questions/start \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test-123"}'

# Test proyecto jurídico
curl -X POST http://localhost:8000/api/ursall/questions/answer \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test-123", "question_id": "tipo_trabajo", "answer": "proyecto"}'
```

---

## Módulos Implementados

1. **`path_mapper_ursall.py`**: Lógica de generación de rutas URSALL
2. **`nlp_extractor_legal.py`**: Extracción NLP para datos legales
3. **`questions_ursall.py`**: Flujo de preguntas URSALL
4. **`main_ursall.py`**: Endpoints API URSALL

Todos integrados en el sistema principal a través de `main.py`.
