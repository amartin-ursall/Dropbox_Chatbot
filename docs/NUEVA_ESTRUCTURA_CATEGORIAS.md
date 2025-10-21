# Nueva Estructura de Categorías: Legal y Seguros

## Fecha: 2025-10-20

## Resumen de Cambios

Se ha implementado una nueva estructura jerárquica de categorización de documentos que incluye dos categorías principales:

1. **Legal** - Incluye Procedimientos Judiciales y Proyectos Jurídicos (URSALL)
2. **Seguros** - Sistema nuevo para gestionar documentación de seguros (provisional)

---

## 1. Flujo de Preguntas Actualizado

### Pregunta Inicial: Categoría

**Nueva primera pregunta:**
- **ID:** `categoria`
- **Pregunta:** "¿A qué categoría pertenece este documento?"
- **Opciones:** `legal` o `seguros`
- **Extractor NLP:** `extract_categoria()` en `nlp_extractor_legal.py`

**Ejemplos de respuestas aceptadas:**
- "Legal", "Es un documento legal", "Judicial"
- "Seguros", "Es una póliza de seguros", "Siniestro"

---

## 2. Categoría LEGAL (URSALL)

### Flujo Existente Mantenido

Después de seleccionar "Legal", el flujo continúa con:

1. **tipo_trabajo** → ¿Procedimiento o Proyecto?
2. **client** → Nombre del cliente

### A) Procedimientos Judiciales (11 preguntas)
- jurisdiccion
- juzgado_num
- demarcacion
- num_procedimiento
- fecha_procedimiento
- partes (parte_a + parte_b)
- materia_proc
- doc_type_proc

### B) Proyectos Jurídicos (7 preguntas)
- proyecto_year
- proyecto_month
- proyecto_nombre
- proyecto_materia
- doc_type_proyecto

**Estructura de carpetas:**
```
/CLIENTE/1. Procedimientos Judiciales/
  AAAA_MM_Juzgado_Demarcación_NºProc/AAAA_ParteA Vs ParteB_Materia/
    01. Escritos presentados/
    02. Resoluciones judiciales/
    ... (10 carpetas estándar)

/CLIENTE/2. Proyectos Jurídicos/
  AAAA_MM_Cliente_Proyecto_Materia/
    00. General/
    01. Documentación recibida/
    ... (8 carpetas estándar)
```

---

## 3. Categoría SEGUROS (NUEVO - Provisional)

### Flujo de Preguntas (6 preguntas)

1. **tipo_seguro** → Tipo de documento de seguros
   - Opciones: póliza, siniestro, comunicación, otro

2. **compania_seguro** → Compañía aseguradora
   - Ejemplos: MAPFRE, AXA, Allianz

3. **tomador_seguro** → Tomador/asegurado
   - Ejemplos: Juan Pérez García, Empresa XYZ SL

4. **ramo_seguro** → Ramo del seguro
   - Ejemplos: Salud, Automóvil, Hogar, Vida

5. **fecha_seguro** → Fecha del documento (YYYY-MM-DD)
   - Formato: 2025-01-15

6. **doc_type_seguro** → Descripción del documento
   - Ejemplos: Póliza original, Parte de siniestro, Recibo de pago

### Estructura de Carpetas (Provisional)

```
/Seguros/[Compañía]/[Ramo]/[Tomador]/[Año]/
  01. Pólizas/
  02. Siniestros/
  03. Comunicaciones/
  04. Otros/
```

**Ejemplo:**
```
/Seguros/MAPFRE/Salud/Juan_Perez_Garcia/2025/
  01. Pólizas/
  02. Siniestros/
  03. Comunicaciones/
  04. Otros/
```

### Nombre de Archivo Generado

**Formato:** `YYYY-MM-DD_TipoSeguro_Descripcion.ext`

**Ejemplo:** `2025-01-15_Poliza_Poliza_original.pdf`

---

## 4. Archivos Modificados

### Backend

#### A) Flujo de Preguntas
- **`backend/app/questions_ursall.py`**
  - Añadida pregunta `categoria` como primera pregunta
  - Añadidas 6 preguntas del flujo Seguros
  - Actualizada función `get_first_question_ursall()` para devolver `categoria`

#### B) Extractores NLP
- **`backend/app/nlp_extractor_legal.py`**
  - Añadida función `extract_categoria()` con keywords para legal/seguros
  - Registrada en `extract_information_legal()`

#### C) Validaciones
- **`backend/app/main.py`**
  - Añadida validación para pregunta `categoria` (líneas 568-589)
  - Modificado endpoint `/api/questions/generate-path` (líneas 706-773)
  - Soporte para generar rutas de Seguros y Legal

#### D) Path Mapper
- **`backend/app/path_mapper_seguros.py`** (NUEVO)
  - Función `suggest_path_seguros()` para generar estructura de Seguros
  - Mapeo de tipo_seguro a subcarpetas

---

## 5. Extractores NLP Añadidos

### `extract_categoria(user_input: str) -> Optional[str]`

**Keywords para "legal":**
- legal, jurídico, judicial, procedimiento, juzgado, tribunal, sentencia, demanda, recurso, proyecto, informe legal, dictamen, asesor, consultoría

**Keywords para "seguros":**
- seguro, póliza, aseguradora, siniestro, prima, cobertura, indemnización, asegurado, tomador, beneficiario, riesgo, franquicia

**Lógica:** Cuenta coincidencias de keywords en ambas listas y devuelve la categoría con más matches.

---

## 6. Retrocompatibilidad

### Comportamiento por Defecto

Si no se proporciona el campo `categoria` en `extracted_answers`, el sistema asume **"legal"** por defecto (línea 727 en main.py):

```python
categoria = extracted_answers.get("categoria", "legal")
```

Esto garantiza que:
- Flujos antiguos sin la pregunta de categoría sigan funcionando
- Documentos históricos se procesen como Legal
- Migraciones sean transparentes

---

## 7. Testing

### Pruebas Ejecutadas

Se crearon tests para validar los extractores NLP:
- **`backend/test_extraction_fixes.py`**
  - Tests para `extract_categoria()`
  - Tests para `extract_tipo_trabajo()`
  - Tests para `extract_juzgado_numero()`

**Resultado:** ✅ Todas las pruebas pasaron

---

## 8. Próximos Pasos Recomendados

### Para Seguros (Sistema Provisional):

1. **Definir estructura final** basada en feedback del equipo
2. **Añadir subcarpetas adicionales** según necesidades reales
3. **Implementar extractores NLP** para tipos de seguro específicos
4. **Validaciones mejoradas** para números de póliza, siniestros, etc.
5. **Integración con Gemini AI** para extracción inteligente de datos de seguros

### Para Legal:

1. **Mantener estructura URSALL** existente
2. **Continuar mejorando extractores NLP** para preguntas legales
3. **Validar estructura de carpetas** con usuarios finales

---

## 9. Ejemplos de Uso

### Ejemplo 1: Documento Legal - Procedimiento

**Usuario:** "Es un documento judicial"
- Categoría: `legal` → Tipo: `procedimiento`
- Ruta generada: `/GRUPO_GORETTI/1. Procedimientos Judiciales/2025_03_SC3_Tenerife_455/...`

### Ejemplo 2: Documento Legal - Proyecto

**Usuario:** "Es un proyecto legal"
- Categoría: `legal` → Tipo: `proyecto`
- Ruta generada: `/GESTIONA_SL/2. Proyectos Jurídicos/2025_06_GESTIONA_SL_Informe_Urbanismo/...`

### Ejemplo 3: Documento de Seguros

**Usuario:** "Es una póliza de seguros"
- Categoría: `seguros`
- Ruta generada: `/Seguros/MAPFRE/Salud/Juan_Perez_Garcia/2025/01. Pólizas/`

---

## 10. Notas Importantes

⚠️ **Sistema de Seguros es PROVISIONAL**
- La estructura propuesta es inicial y debe validarse con el equipo
- Las preguntas pueden ajustarse según necesidades reales
- La organización de carpetas puede modificarse

✅ **Sistema Legal (URSALL) es ESTABLE**
- Estructura validada y en producción
- No se modificó la lógica existente
- Totalmente retrocompatible

---

## Autor

Claude Code - Solución implementada el 2025-10-20

## Changelog

- **v1.0 (2025-10-20)**: Implementación inicial con categorías Legal y Seguros
