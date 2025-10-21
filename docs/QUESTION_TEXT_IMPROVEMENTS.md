# Question Text Improvements for Natural Language Support

**Date:** 2025-01-20
**Status:** ✅ Implemented and Tested

## Problem

The user reported that the system was still too restrictive, forcing exact keyword inputs like "procedimiento" or "proyecto" even though the backend supported natural language interpretation.

**Root Cause:** The question text itself was instructing users to type exact keywords:
```
"¿Es un Procedimiento Judicial o un Proyecto Jurídico? (escribe: procedimiento o proyecto)"
```

This created a poor user experience where users felt forced to use specific keywords despite the system's natural language capabilities.

## Solution

Updated question texts and examples to be more open and encourage natural language responses.

## Changes Made

### 1. `tipo_trabajo` Question

**Before:**
```python
"question_text": "¿Es un Procedimiento Judicial o un Proyecto Jurídico? (escribe: procedimiento o proyecto)",
"help_text": "Selecciona 'procedimiento' para documentos relacionados con casos judiciales...",
"examples": ["procedimiento", "proyecto"]
```

**After:**
```python
"question_text": "¿De qué tipo de trabajo se trata?",
"help_text": "Puedes responder con lenguaje natural. Por ejemplo: 'Es un juicio', 'Procedimiento judicial', 'Es un proyecto de asesoría', 'Informe legal', etc. El sistema interpretará tu respuesta.",
"examples": [
    "Es un procedimiento judicial",
    "Un juicio en el juzgado social",
    "Es un proyecto de asesoría legal",
    "Informe jurídico para cliente",
    "Demanda laboral",
    "Proyecto de consultoría"
]
```

### 2. `jurisdiccion` Question

**Before:**
```python
"question_text": "¿Qué tipo de juzgado es? (contencioso, social, civil, penal, instrucción)",
"help_text": "Selecciona la jurisdicción del procedimiento...",
"examples": ["social", "contencioso administrativo", "Juzgado de lo Social"]
```

**After:**
```python
"question_text": "¿Qué tipo de juzgado o jurisdicción es?",
"help_text": "Puedes responder con lenguaje natural. El sistema interpreta: 'social', 'juzgado de lo social', 'contencioso', 'contencioso-administrativo', 'civil', 'penal', 'instrucción', etc.",
"examples": [
    "social",
    "Juzgado de lo Social",
    "contencioso administrativo",
    "Juzgado de lo Contencioso-Administrativo",
    "civil",
    "penal",
    "instrucción"
]
```

### 3. `doc_type_proc` Question

**Before:**
```python
"question_text": "¿Tipo de documento? (ej: Escrito, Sentencia, Pericial, Notificación)",
"help_text": "El tipo de documento determinará la subcarpeta donde se guardará...",
"examples": ["Sentencia", "Escrito de demanda", "Informe pericial", "Notificación del juzgado"]
```

**After:**
```python
"question_text": "¿Qué tipo de documento judicial es?",
"help_text": "Describe el documento con lenguaje natural. Ejemplos: 'Es una demanda', 'Sentencia del juzgado', 'Recurso de apelación', 'Informe pericial', etc. El sistema lo clasificará automáticamente.",
"examples": [
    "Es una demanda",
    "Sentencia del juzgado",
    "Recurso de apelación",
    "Escrito de contestación",
    "Informe pericial",
    "Notificación judicial",
    "Auto del juzgado"
]
```

### 4. `doc_type_proyecto` Question

**Before:**
```python
"question_text": "¿Tipo de documento? (ej: Informe, Borrador, Contrato, Comunicación)",
"help_text": "El tipo de documento determinará la subcarpeta donde se guardará...",
"examples": ["Informe", "Borrador", "Contrato", "Comunicación"]
```

**After:**
```python
"question_text": "¿Qué tipo de documento es este proyecto?",
"help_text": "Describe el documento con lenguaje natural. Ejemplos: 'Es un informe jurídico', 'Borrador de contrato', 'Dictamen legal', 'Comunicación al cliente', etc. El sistema lo clasificará automáticamente.",
"examples": [
    "Es un informe jurídico",
    "Borrador de contrato",
    "Dictamen legal",
    "Opinión legal",
    "Comunicación al cliente",
    "Documento de trabajo",
    "Memoria del proyecto"
]
```

## Key Improvements

### 1. **Question Text**
- Removed restrictive instructions like "(escribe: procedimiento o proyecto)"
- Made questions more open-ended and conversational
- Focused on "what" rather than "how to answer"

### 2. **Help Text**
- Explicitly states "Puedes responder con lenguaje natural"
- Emphasizes that the system will interpret the response
- Removes technical jargon about validation rules

### 3. **Examples**
- Changed from single-word examples to full natural language sentences
- Increased number of examples from 2-3 to 6-7
- Show variety of ways to express the same intent
- Include both formal and informal phrasings

## User Experience Impact

### Before
```
System: ¿Es un Procedimiento Judicial o un Proyecto Jurídico? (escribe: procedimiento o proyecto)
User: "es un juicio"
System: ❌ Error (user feels restricted)
```

### After
```
System: ¿De qué tipo de trabajo se trata?
        Puedes responder con lenguaje natural. Por ejemplo: 'Es un juicio',
        'Procedimiento judicial', 'Es un proyecto de asesoría', etc.
User: "es un juicio"
System: ✅ Interpretado como 'procedimiento' (seamless experience)
```

## Testing

All natural language tests pass successfully:

```bash
cd backend
.\venv\Scripts\python.exe test_nl_interpretation.py
```

**Results:** 16/16 tests passing ✅

### Test Coverage
- Direct keywords: "procedimiento", "proyecto"
- Natural language: "es un juicio", "proyecto de asesoría", "informe legal"
- Ambiguous inputs: "no sé", "quizás"
- Document types: "Es una demanda", "Recurso de apelación"

## Files Modified

1. **backend/app/questions_ursall.py**
   - Lines 11-26: `tipo_trabajo` question
   - Lines 46-63: `jurisdiccion` question
   - Lines 131-148: `doc_type_proc` question
   - Lines 196-213: `doc_type_proyecto` question

## Design Principles Applied

1. **User-Centric Language**
   - Questions ask "what" instead of "how"
   - Natural phrasing that matches how users think

2. **Progressive Disclosure**
   - Main question is simple
   - Help text provides guidance
   - Examples show possibilities

3. **Flexibility First**
   - Accept multiple forms of the same answer
   - Don't force specific formats unless necessary
   - Let AI handle interpretation

4. **Clear Feedback**
   - Examples show what's acceptable
   - Help text explains system capabilities
   - Error messages guide users when needed

## Related Documentation

- `docs/NATURAL_LANGUAGE_IMPROVEMENTS.md` - Backend natural language implementation
- `backend/app/gemini_rest_extractor.py` - AI extraction logic
- `backend/app/nlp_extractor_legal.py` - NLP fallback logic
- `docs/URSALL_IMPLEMENTATION.md` - Overall URSALL system documentation

## Future Enhancements

1. **Context-Aware Help**
   - Show examples based on previous answers
   - Provide dynamic suggestions

2. **Voice Input Support**
   - Speech-to-text integration
   - Natural spoken language processing

3. **Multi-Language**
   - English, Portuguese support
   - Automatic language detection

4. **Learning System**
   - Track which phrasings users prefer
   - Update examples based on usage patterns

---

**Status:** Production Ready ✅
**User Experience:** Significantly Improved
**Flexibility:** Maximum natural language support
**Backend Support:** Fully compatible with existing AI/NLP extraction
