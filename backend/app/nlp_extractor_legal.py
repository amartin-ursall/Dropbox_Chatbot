"""
NLP Extractor Legal - Extracción de información para documentos legales URSALL
Extrae información específica de procedimientos judiciales y proyectos jurídicos
"""
import re
from typing import Optional, Dict
from datetime import datetime


# Patrones para jurisdicciones
JURISDICCION_PATTERNS = [
    r'(?:juzgado|jurisdicción|jurisdiccion)\s+(?:de\s+lo\s+)?(?:contencioso[-\s]?administrativo|contencioso)',
    r'(?:juzgado|jurisdicción|jurisdiccion)\s+(?:de\s+lo\s+)?(?:social|laboral)',
    r'(?:juzgado|jurisdicción|jurisdiccion)\s+(?:de\s+)?(?:primera\s+instancia|civil)',
    r'(?:juzgado|jurisdicción|jurisdiccion)\s+(?:de\s+)?(?:penal|instrucción|instruccion)',
    r'\b(contencioso|social|civil|penal|instrucción|instruccion)\b',
]

# Patrones para número de juzgado
JUZGADO_NUM_PATTERNS = [
    r'(?:juzgado|jdo\.?)\s+(?:n[úuº°]?\s*)?(\d+)',
    r'(?:número|numero|nº|n\.?)\s*(\d+)',
    r'\b([A-Z]{2,3})(\d+)\b',  # Ej: CA1, SC2, CIV4
]

# Patrones para demarcación
DEMARCACION_PATTERNS = [
    r'(?:de\s+)([A-ZÁÉÍÓÚ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóúñ]+)?)',  # "de Santa Cruz", "de Tenerife"
    r'\b(Santa\s+Cruz|Tenerife|Las\s+Palmas|La\s+Gomera|San\s+Sebastián|La\s+Laguna)\b',
]

# Patrones para número de procedimiento
NUM_PROCEDIMIENTO_PATTERNS = [
    r'(?:procedimiento|proc\.?|autos?|n[úuº°]?)\s*(\d+/\d{4})',
    r'(\d+/\d{4})',
    r'(?:número|numero|nº)\s*(\d+)',
]

# Patrones para partes (actor vs demandado)
PARTES_PATTERNS = [
    r'([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.]+)\s+(?:vs\.?|contra|c\/)\s+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.]+)',
    r'(?:actor|demandante)[:\s]+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.]+)',
    r'(?:demandado|demandada)[:\s]+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.]+)',
]

# Patrones para materia
MATERIA_PATTERNS = [
    r'(?:materia|asunto|sobre|relativo\s+a)[:\s]+([A-ZÁÉÍÓÚ][a-záéíóúñ]+)',
    r'(?:despido|fijeza|urbanismo|reclamación|indemnización|art\.?\s*\d+)',
]


def extract_jurisdiccion(user_input: str) -> Optional[str]:
    """
    Extrae la jurisdicción del texto

    Ejemplos:
    - "Juzgado de lo Contencioso-Administrativo" → "contencioso"
    - "Social" → "social"
    - "Juzgado de Primera Instancia" → "civil"
    """
    user_input_lower = user_input.lower()

    # Buscar patrones específicos
    if re.search(r'contencioso[-\s]?administrativo|contencioso', user_input_lower):
        return "contencioso"
    elif re.search(r'social|laboral', user_input_lower):
        return "social"
    elif re.search(r'civil|primera\s+instancia', user_input_lower):
        return "civil"
    elif re.search(r'penal(?!\s*(mercantil|administrativo))', user_input_lower):
        return "penal"
    elif re.search(r'instrucción|instruccion', user_input_lower):
        return "instrucción"

    # Buscar palabra clave sola
    for pattern in JURISDICCION_PATTERNS:
        match = re.search(pattern, user_input_lower)
        if match:
            if match.groups():
                return match.group(1).strip()

    return None


def extract_juzgado_numero(user_input: str) -> Optional[str]:
    """
    Extrae el número del juzgado

    Ejemplos:
    - "Juzgado nº 2" → "2"
    - "CA1" → "1"
    - "Juzgado Social 3" → "3"
    """
    for pattern in JUZGADO_NUM_PATTERNS:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:
                # Patrón tipo "CA1"
                return match.group(2)
            else:
                return match.group(1)

    return None


def extract_demarcacion(user_input: str) -> Optional[str]:
    """
    Extrae la demarcación del juzgado

    Ejemplos:
    - "Juzgado de Santa Cruz" → "SantaCruz"
    - "de Tenerife" → "Tenerife"
    - "La Gomera" → "LaGomera"
    """
    for pattern in DEMARCACION_PATTERNS:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            demarcacion = match.group(1).strip()
            # Eliminar espacios para el nombre de carpeta
            return demarcacion.replace(" ", "")

    return None


def extract_num_procedimiento(user_input: str) -> Optional[str]:
    """
    Extrae el número de procedimiento

    Ejemplos:
    - "Procedimiento 455/2025" → "455/2025"
    - "Autos 123/2025" → "123/2025"
    - "455/2025" → "455/2025"
    """
    for pattern in NUM_PROCEDIMIENTO_PATTERNS:
        match = re.search(pattern, user_input)
        if match:
            num_proc = match.group(1)
            # Separar número y año si están juntos
            if '/' in num_proc:
                return num_proc
            else:
                # Buscar año cercano
                year_match = re.search(r'/(\d{4})', user_input)
                if year_match:
                    return f"{num_proc}/{year_match.group(1)}"
                return num_proc

    return None


def extract_partes(user_input: str) -> Dict[str, Optional[str]]:
    """
    Extrae las partes del procedimiento (actor y demandado)

    Ejemplos:
    - "Pedro Perez vs Cabildo Gomera" → {"parte_a": "Pedro Perez", "parte_b": "Cabildo Gomera"}
    - "Actor: Juan López, Demandado: Motor 7 Islas" → {"parte_a": "Juan López", "parte_b": "Motor 7 Islas"}
    """
    result = {"parte_a": None, "parte_b": None}

    # Patrón "A vs B"
    match = re.search(r'([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.&,]+)\s+(?:vs\.?|contra|c\/)\s+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.&,]+)', user_input, re.IGNORECASE)
    if match:
        result["parte_a"] = match.group(1).strip()
        result["parte_b"] = match.group(2).strip()
        return result

    # Buscar actor/demandante
    actor_match = re.search(r'(?:actor|demandante)[:\s]+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.&,]+?)(?:\s*,|\s*y|\s*$)', user_input, re.IGNORECASE)
    if actor_match:
        result["parte_a"] = actor_match.group(1).strip()

    # Buscar demandado
    demandado_match = re.search(r'(?:demandado|demandada)[:\s]+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.&,]+?)(?:\s*,|\s*y|\s*$)', user_input, re.IGNORECASE)
    if demandado_match:
        result["parte_b"] = demandado_match.group(1).strip()

    return result


def extract_materia(user_input: str) -> Optional[str]:
    """
    Extrae la materia del procedimiento

    Ejemplos:
    - "Materia: Despido" → "Despidos"
    - "sobre fijeza" → "Fijeza"
    - "Art 316 CP" → "Art316CP"
    """
    user_input_lower = user_input.lower()

    # Buscar materias comunes
    materias_comunes = {
        'despido': 'Despidos',
        'fijeza': 'Fijeza',
        'urbanismo': 'Urbanismo',
        'reclamación': 'ReclamacionCantidad',
        'reclamacion': 'ReclamacionCantidad',
        'indemnización': 'Indemnizacion',
        'indemnizacion': 'Indemnizacion',
    }

    for key, value in materias_comunes.items():
        if key in user_input_lower:
            return value

    # Buscar artículo del código penal
    art_match = re.search(r'art(?:ículo|iculo)?\.?\s*(\d+)\s*(?:CP|C\.?P\.?)', user_input, re.IGNORECASE)
    if art_match:
        return f"Art{art_match.group(1)}CP"

    # Buscar patrón "materia: X"
    materia_match = re.search(r'(?:materia|asunto|sobre)[:\s]+([A-ZÁÉÍÓÚ][a-záéíóúñ]+)', user_input, re.IGNORECASE)
    if materia_match:
        materia = materia_match.group(1).strip()
        # Normalizar: sin tildes, sin artículos
        import unicodedata
        materia = unicodedata.normalize('NFD', materia).encode('ascii', 'ignore').decode('utf-8')
        return materia.capitalize()

    return None


def extract_proyecto_info(user_input: str, tipo: str) -> Optional[str]:
    """
    Extrae información de proyectos jurídicos

    Args:
        user_input: Texto del usuario
        tipo: "nombre" o "materia"

    Ejemplos:
    - tipo="nombre": "Informe sobre seguros" → "Informe"
    - tipo="materia": "sobre Seguro de Salud" → "SeguroSalud"
    """
    if tipo == "nombre":
        # Buscar tipo de proyecto
        proyectos = ['informe', 'dictamen', 'estudio', 'analisis', 'análisis', 'consulta']
        for proyecto in proyectos:
            if proyecto in user_input.lower():
                return proyecto.capitalize()

        # Si no se encuentra, extraer primera palabra significativa
        words = user_input.split()
        for word in words:
            if len(word) > 3 and word[0].isupper():
                return word

    elif tipo == "materia":
        # Eliminar palabras comunes y normalizar
        cleaned = re.sub(r'^(sobre|relativo\s+a|en\s+materia\s+de)\s+', '', user_input, flags=re.IGNORECASE)
        cleaned = cleaned.strip()

        # Normalizar: sin tildes, sin espacios, CamelCase
        import unicodedata
        normalized = unicodedata.normalize('NFD', cleaned).encode('ascii', 'ignore').decode('utf-8')

        # Convertir a CamelCase
        words = normalized.split()
        camel_case = ''.join(word.capitalize() for word in words)

        return camel_case if camel_case else None

    return None


def extract_information_legal(question_id: str, user_input: str) -> any:
    """
    Función principal de extracción para datos legales

    Args:
        question_id: Identificador de la pregunta
        user_input: Respuesta del usuario

    Returns:
        Información extraída según el tipo de pregunta
    """
    extractors = {
        "jurisdiccion": extract_jurisdiccion,
        "juzgado_numero": extract_juzgado_numero,
        "demarcacion": extract_demarcacion,
        "num_procedimiento": extract_num_procedimiento,
        "partes": extract_partes,
        "materia": extract_materia,
        "proyecto_nombre": lambda x: extract_proyecto_info(x, "nombre"),
        "proyecto_materia": lambda x: extract_proyecto_info(x, "materia"),
    }

    extractor = extractors.get(question_id)
    if extractor:
        return extractor(user_input)

    return user_input.strip()
