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

# Patrones para número de juzgado (orden de especificidad)
JUZGADO_NUM_PATTERNS = [
    r'(?:juzgado|jdo\.?)\s+(?:n[úuº°]?\s*|numero\s+|número\s+)?(\d+)',  # "juzgado numero 2", "juzgado nº 2"
    r'(?:juzgado|jdo\.?)\s+(?:social|contencioso|civil|penal|instrucción|instruccion)\s+(\d+)',  # "Juzgado Social 4"
    r'(?:número|numero|nº|n\.?)\s+(?:del?\s+juzgado\s+)?(\d+)',  # "numero 2", "número del juzgado 2"
    r'(?:es\s+el\s+)?(?:juzgado\s+)?(?:numero|número)\s+(\d+)',  # "es el juzgado numero 2"
    r'\b([A-Z]{2,3})(\d+)\b',  # "CA1", "SC2" (dos grupos)
    r'^\s*(\d+)\s*$',  # Solo un número (ej: "2", " 3 ")
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
    r'([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.]+)\s+(?:vs\.?|contra|c\/|\/)\s+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.]+)',
    r'(?:actor|demandante|parte\s+a)[:\s]+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.]+)',
    r'(?:demandado|demandada|parte\s+b)[:\s]+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.]+)',
]

# Patrones para materia
MATERIA_PATTERNS = [
    r'(?:materia|asunto|sobre|relativo\s+a)[:\s]+([A-ZÁÉÍÓÚ][a-záéíóúñ]+)',
    r'(?:despido|fijeza|urbanismo|reclamación|indemnización|art\.?\s*\d+)',
]


def extract_categoria(user_input: str) -> Optional[str]:
    """
    Extrae la categoría principal (legal o seguros)

    Ejemplos:
    - "es un documento legal" → "legal"
    - "judicial" → "legal"
    - "es una póliza de seguros" → "seguros"
    - "siniestro" → "seguros"
    """
    user_input_lower = user_input.lower().strip()

    # Palabras clave para Legal
    legal_keywords = [
        "legal", "juridico", "jurídico", "judicial", "procedimiento",
        "juzgado", "tribunal", "jurisdicción", "jurisdiccion",
        "contencioso", "social", "civil", "penal", "instrucción", "instruccion",
        "sentencia", "auto", "providencia", "demanda", "recurso",
        "proyecto", "informe legal", "dictamen", "asesor", "consultoria"
    ]

    # Palabras clave para Seguros
    seguros_keywords = [
        "seguro", "seguros", "poliza", "póliza", "aseguradora",
        "siniestro", "prima", "cobertura", "indemnizacion", "indemnización",
        "asegurado", "tomador", "beneficiario", "riesgo", "franquicia"
    ]

    # Contar coincidencias
    legal_matches = sum(1 for kw in legal_keywords if kw in user_input_lower)
    seguros_matches = sum(1 for kw in seguros_keywords if kw in user_input_lower)

    # Decidir basado en coincidencias
    if legal_matches > seguros_matches:
        return "legal"
    elif seguros_matches > legal_matches:
        return "seguros"

    # Si hay empate o ninguna coincidencia, devolver None
    return None


def extract_tipo_trabajo(user_input: str) -> Optional[str]:
    """
    Extrae el tipo de trabajo (procedimiento o proyecto)

    Ejemplos:
    - "es un documento judicial" → "procedimiento"
    - "procedimiento judicial" → "procedimiento"
    - "proyecto de asesoría" → "proyecto"
    - "informe legal" → "proyecto"
    - "judicial" → "procedimiento"
    """
    user_input_lower = user_input.lower().strip()

    # Palabras clave para procedimiento judicial
    procedimiento_keywords = [
        "procedimiento", "judicial", "juicio", "demanda", "recurso",
        "juzgado", "tribunal", "jurisdicción", "jurisdiccion",
        "contencioso", "social", "civil", "penal", "instrucción", "instruccion",
        "sentencia", "auto", "providencia", "notificación", "notificacion",
        "autos", "pleito", "litigio", "causa"
    ]

    # Palabras clave para proyecto jurídico
    proyecto_keywords = [
        "proyecto", "asesor", "consultoria", "consultoría",
        "opinion", "opinión", "informe", "dictamen", "estudio",
        "analisis", "análisis", "consulta", "asesoramiento"
    ]

    # Contar coincidencias de cada tipo
    proc_matches = sum(1 for kw in procedimiento_keywords if kw in user_input_lower)
    proy_matches = sum(1 for kw in proyecto_keywords if kw in user_input_lower)

    # Decidir basado en coincidencias
    if proc_matches > proy_matches:
        return "procedimiento"
    elif proy_matches > proc_matches:
        return "proyecto"

    # Si hay empate o ninguna coincidencia, devolver None para que main.py maneje el error
    return None


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
    - "Parte A: Empresa XYZ / Parte B: Ayuntamiento" → {"parte_a": "Empresa XYZ", "parte_b": "Ayuntamiento"}
    """
    result = {"parte_a": None, "parte_b": None}

    # Si el input está vacío o no es válido, devolver None para ambos campos
    if not user_input or len(user_input.strip()) < 3:
        return result

    # Patrón "A vs B" o "A / B"
    match = re.search(r'([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.&,]+)\s+(?:vs\.?|contra|c\/|\/)\s+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.&,]+)', user_input, re.IGNORECASE)
    if match:
        result["parte_a"] = match.group(1).strip()
        result["parte_b"] = match.group(2).strip()
        return result

    # Buscar actor/demandante/parte_a
    actor_match = re.search(r'(?:actor|demandante|parte\s+a)[:\s]+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.&,]+?)(?:\s*,|\s*y|\s*$|\s*\/)', user_input, re.IGNORECASE)
    if actor_match:
        result["parte_a"] = actor_match.group(1).strip()

    # Buscar demandado/parte_b
    demandado_match = re.search(r'(?:demandado|demandada|parte\s+b)[:\s]+([A-ZÁÉÍÓÚ][a-záéíóúñ\s\.&,]+?)(?:\s*,|\s*y|\s*$)', user_input, re.IGNORECASE)
    if demandado_match:
        result["parte_b"] = demandado_match.group(1).strip()

    # Si no se pudo extraer alguna de las partes, asignar valores por defecto
    if not result["parte_a"]:
        result["parte_a"] = "Parte Actora"
    
    if not result["parte_b"]:
        result["parte_b"] = "Parte Demandada"

    return result


def extract_materia(user_input: str) -> Optional[str]:
    """
    Extrae la materia del procedimiento con normalización mejorada

    Ejemplos:
    - "Materia: Despido" → "Despidos"
    - "materia de Despidos" → "Despidos"
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

    # Buscar patrón "materia: X" o "materia de X"
    materia_match = re.search(r'(?:materia|asunto)(?:\s+de)?\s*:?\s*([A-ZÁÉÍÓÚ][a-záéíóúñ]+)', user_input, re.IGNORECASE)
    if materia_match:
        materia = materia_match.group(1).strip()
        # Normalizar: sin tildes, sin artículos
        import unicodedata
        materia = unicodedata.normalize('NFD', materia).encode('ascii', 'ignore').decode('utf-8')
        return materia.capitalize()

    # Si no hay patrón específico, devolver el input limpio
    return None


def extract_year(user_input: str) -> Optional[str]:
    """
    Extrae año de texto en lenguaje natural

    Ejemplos:
    - "año 2025" → "2025"
    - "2025" → "2025"
    - "en el año 2024" → "2024"
    """
    # Buscar año de 4 dígitos
    year_match = re.search(r'\b(20\d{2})\b', user_input)
    if year_match:
        return year_match.group(1)

    return None


def extract_month(user_input: str) -> Optional[str]:
    """
    Extrae mes y lo normaliza a formato MM

    Ejemplos:
    - "mes de agosto" → "08"
    - "agosto" → "08"
    - "08" → "08"
    - "mes 8" → "08"
    """
    # Mapeo de meses en español
    meses = {
        'enero': '01', 'ene': '01',
        'febrero': '02', 'feb': '02',
        'marzo': '03', 'mar': '03',
        'abril': '04', 'abr': '04',
        'mayo': '05', 'may': '05',
        'junio': '06', 'jun': '06',
        'julio': '07', 'jul': '07',
        'agosto': '08', 'ago': '08',
        'septiembre': '09', 'sep': '09', 'sept': '09',
        'octubre': '10', 'oct': '10',
        'noviembre': '11', 'nov': '11',
        'diciembre': '12', 'dic': '12',
    }

    user_input_lower = user_input.lower()

    # Buscar nombre de mes
    for mes_name, mes_num in meses.items():
        if mes_name in user_input_lower:
            return mes_num

    # Buscar número de mes
    mes_num_match = re.search(r'\b(0?[1-9]|1[0-2])\b', user_input)
    if mes_num_match:
        mes = mes_num_match.group(1)
        # Normalizar a dos dígitos
        return mes.zfill(2)

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
        "categoria": extract_categoria,  # ← NUEVO: Extractor para categoría
        "tipo_trabajo": extract_tipo_trabajo,  # Extractor para tipo de trabajo
        "jurisdiccion": extract_jurisdiccion,
        "juzgado_num": extract_juzgado_numero,
        "juzgado_numero": extract_juzgado_numero,  # Alias
        "demarcacion": extract_demarcacion,
        "num_procedimiento": extract_num_procedimiento,
        "partes": extract_partes,
        "materia": extract_materia,
        "materia_proc": extract_materia,
        "proyecto_year": extract_year,
        "proyecto_month": extract_month,
        "proyecto_nombre": lambda x: extract_proyecto_info(x, "nombre"),
        "proyecto_materia": lambda x: extract_proyecto_info(x, "materia"),
    }

    extractor = extractors.get(question_id)
    if extractor:
        return extractor(user_input)

    return user_input.strip()
