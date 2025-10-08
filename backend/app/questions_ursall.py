"""
Question flow logic for URSALL Legal structure
Maneja dos flujos: Procedimientos Judiciales y Proyectos Jurídicos
"""
from typing import Dict, Optional, List, Any


# Definición de flujos de preguntas para URSALL
QUESTIONS_URSALL = {
    # Pregunta inicial: determinar tipo de trabajo
    "tipo_trabajo": {
        "question_id": "tipo_trabajo",
        "question_text": "¿Es un Procedimiento Judicial o un Proyecto Jurídico? (escribe: procedimiento o proyecto)",
        "required": True,
        "validation": {"type": "choice", "choices": ["procedimiento", "proyecto"]},
        "next": "client",
        "help_text": "Selecciona 'procedimiento' para documentos relacionados con casos judiciales o 'proyecto' para trabajos jurídicos no judiciales.",
        "examples": ["procedimiento", "proyecto"]
    },

    # Cliente (común para ambos flujos)
    "client": {
        "question_id": "client",
        "question_text": "¿Cuál es el nombre del cliente? (ej: GRUPO GORETTI, JJ. TEALQUILA Y GESTIONA SL)",
        "required": True,
        "validation": {"min_length": 2},
        "next_conditional": {
            "tipo_trabajo": {
                "procedimiento": "jurisdiccion",
                "proyecto": "proyecto_year"
            }
        },
        "help_text": "Introduce el nombre completo del cliente. Para grupos empresariales, usa el formato 'GRUPO + NOMBRE'.",
        "examples": ["GRUPO GORETTI", "JJ. TEALQUILA Y GESTIONA SL", "Ayuntamiento Adeje"]
    },

    # ============= FLUJO PROCEDIMIENTO JUDICIAL =============

    "jurisdiccion": {
        "question_id": "jurisdiccion",
        "question_text": "¿Qué tipo de juzgado es? (contencioso, social, civil, penal, instrucción)",
        "required": True,
        "validation": {"type": "choice", "choices": ["contencioso", "social", "civil", "penal", "instrucción", "instruccion"]},
        "next": "juzgado_num",
        "flow": "procedimiento",
        "help_text": "Selecciona la jurisdicción del procedimiento. Esto determinará la abreviatura en la ruta (CA, SC, CIV, PEN, JPI).",
        "examples": ["social", "contencioso administrativo", "Juzgado de lo Social"]
    },

    "juzgado_num": {
        "question_id": "juzgado_num",
        "question_text": "¿Número del juzgado? (ej: 1, 2, 3)",
        "required": True,
        "validation": {"type": "number"},
        "next": "demarcacion",
        "flow": "procedimiento",
        "help_text": "Introduce solo el número del juzgado, sin texto adicional.",
        "examples": ["2", "Número 3", "Juzgado 5"]
    },

    "demarcacion": {
        "question_id": "demarcacion",
        "question_text": "¿Demarcación del juzgado? (ej: Santa Cruz, Tenerife, La Gomera)",
        "required": True,
        "validation": {"min_length": 2},
        "next": "num_procedimiento",
        "flow": "procedimiento",
        "help_text": "Introduce la demarcación geográfica donde se encuentra el juzgado.",
        "examples": ["Tenerife", "Santa Cruz", "La Gomera"]
    },

    "num_procedimiento": {
        "question_id": "num_procedimiento",
        "question_text": "¿Número de procedimiento/autos? (ej: 455/2025, 245/2025)",
        "required": True,
        "validation": {"pattern": r"^\d+/\d{4}$"},
        "next": "fecha_procedimiento",
        "flow": "procedimiento",
        "help_text": "Introduce el número de procedimiento en formato XXX/YYYY. Este dato es crucial para la estructura de carpetas.",
        "examples": ["455/2025", "Procedimiento 123/2024", "Autos 789/2023"]
    },

    "fecha_procedimiento": {
        "question_id": "fecha_procedimiento",
        "question_text": "¿Fecha del procedimiento? (formato: YYYY-MM-DD)",
        "required": True,
        "validation": {"format": "date"},
        "next": "partes",
        "flow": "procedimiento",
        "help_text": "Introduce la fecha en formato YYYY-MM-DD. Esta fecha se usará para el nombre del archivo.",
        "examples": ["2025-08-15", "2024-03-22"]
    },

    "partes": {
        "question_id": "partes",
        "question_text": "¿Quiénes son las partes del procedimiento? (formato: Parte A vs Parte B)",
        "required": True,
        "validation": {"min_length": 5},
        "next": "materia_proc",
        "flow": "procedimiento",
        "help_text": "Introduce las partes separadas por 'vs', 'contra', o similar. El sistema extraerá automáticamente parte_a y parte_b.",
        "examples": ["Pedro Perez vs Cabildo Gomera", "Ministerio Fiscal contra Juan García", "Actor: Empresa XYZ / Demandado: Ayuntamiento"]
    },

    "materia_proc": {
        "question_id": "materia_proc",
        "question_text": "¿Materia del procedimiento? (ej: Despidos, Fijeza, Urbanismo, Art316CP)",
        "required": True,
        "validation": {"min_length": 2},
        "next": "doc_type_proc",
        "flow": "procedimiento",
        "help_text": "Introduce la materia o asunto principal del procedimiento. Será parte del nombre de la carpeta.",
        "examples": ["Despidos", "Fijeza", "Urbanismo", "Art316CP"]
    },

    "doc_type_proc": {
        "question_id": "doc_type_proc",
        "question_text": "¿Tipo de documento? (ej: Escrito, Sentencia, Pericial, Notificación)",
        "required": True,
        "validation": {"min_length": 2},
        "next": None,  # Última pregunta del flujo procedimiento
        "flow": "procedimiento",
        "help_text": "El tipo de documento determinará la subcarpeta donde se guardará. Consulta la tabla de mapeo en la documentación.",
        "examples": ["Sentencia", "Escrito de demanda", "Informe pericial", "Notificación del juzgado"]
    },

    # ============= FLUJO PROYECTO JURÍDICO =============

    "proyecto_year": {
        "question_id": "proyecto_year",
        "question_text": "¿Año del proyecto? (formato: YYYY)",
        "required": True,
        "validation": {"pattern": r"^\d{4}$"},
        "next": "proyecto_month",
        "flow": "proyecto",
        "help_text": "Introduce el año del proyecto en formato de 4 dígitos (YYYY).",
        "examples": ["2025", "2024"]
    },

    "proyecto_month": {
        "question_id": "proyecto_month",
        "question_text": "¿Mes del proyecto? (formato: MM, ej: 01, 06, 12)",
        "required": True,
        "validation": {"pattern": r"^(0[1-9]|1[0-2])$"},
        "next": "proyecto_nombre",
        "flow": "proyecto",
        "help_text": "Introduce el mes en formato de 2 dígitos (MM). Usa 01 para enero, 06 para junio, etc.",
        "examples": ["01", "06", "12"]
    },

    "proyecto_nombre": {
        "question_id": "proyecto_nombre",
        "question_text": "¿Nombre del proyecto? (ej: Informe, Dictamen, Estudio)",
        "required": True,
        "validation": {"min_length": 2},
        "next": "proyecto_materia",
        "flow": "proyecto",
        "help_text": "Introduce un nombre descriptivo y conciso para el proyecto.",
        "examples": ["Informe", "Dictamen", "Estudio", "Consulta"]
    },

    "proyecto_materia": {
        "question_id": "proyecto_materia",
        "question_text": "¿Materia del proyecto? (ej: Seguro Salud, Urbanismo, Laboral)",
        "required": True,
        "validation": {"min_length": 2},
        "next": "doc_type_proyecto",
        "flow": "proyecto",
        "help_text": "Introduce la materia o asunto principal del proyecto. Será parte del nombre de la carpeta.",
        "examples": ["Seguro Salud", "Urbanismo", "Laboral", "Contratación Pública"]
    },

    "doc_type_proyecto": {
        "question_id": "doc_type_proyecto",
        "question_text": "¿Tipo de documento? (ej: Informe, Borrador, Contrato, Comunicación)",
        "required": True,
        "validation": {"min_length": 2},
        "next": None,  # Última pregunta del flujo proyecto
        "flow": "proyecto",
        "help_text": "El tipo de documento determinará la subcarpeta donde se guardará. Consulta la tabla de mapeo en la documentación.",
        "examples": ["Informe", "Borrador", "Contrato", "Comunicación"]
    },
}


def get_first_question_ursall() -> Dict:
    """Obtener la primera pregunta del flujo URSALL"""
    question = QUESTIONS_URSALL["tipo_trabajo"].copy()
    question.pop("next", None)
    question.pop("next_conditional", None)
    return question


def get_next_question_ursall(current_question_id: str, answers: Dict[str, str]) -> Optional[Dict]:
    """
    Obtener la siguiente pregunta basada en el contexto de respuestas

    Args:
        current_question_id: ID de la pregunta actual
        answers: Diccionario con todas las respuestas hasta ahora

    Returns:
        Siguiente pregunta o None si se completó el flujo
    """
    current = QUESTIONS_URSALL.get(current_question_id)
    if not current:
        return None

    # Manejar siguiente pregunta condicional
    if "next_conditional" in current:
        # La siguiente pregunta depende de una respuesta previa
        for condition_key, condition_values in current["next_conditional"].items():
            condition_answer = answers.get(condition_key, "").lower().strip()
            next_id = condition_values.get(condition_answer)
            if next_id:
                next_question = QUESTIONS_URSALL[next_id].copy()
                next_question.pop("next", None)
                next_question.pop("next_conditional", None)
                return next_question

    # Siguiente pregunta estática
    next_id = current.get("next")
    if not next_id:
        return None

    next_question = QUESTIONS_URSALL[next_id].copy()
    next_question.pop("next", None)
    next_question.pop("next_conditional", None)
    return next_question


def is_last_question_ursall(question_id: str) -> bool:
    """Verificar si es la última pregunta del flujo"""
    question = QUESTIONS_URSALL.get(question_id)
    return question is not None and question.get("next") is None and "next_conditional" not in question


def get_question_flow(question_id: str) -> Optional[str]:
    """Obtener el flujo al que pertenece una pregunta (procedimiento o proyecto)"""
    question = QUESTIONS_URSALL.get(question_id)
    return question.get("flow") if question else None


def validate_ursall_answers(answers: Dict[str, str]) -> Dict[str, any]:
    """
    Validar que todas las respuestas necesarias estén presentes

    Returns:
        Dict con:
        - valid: bool
        - missing: lista de campos faltantes
        - tipo_trabajo: procedimiento o proyecto
    """
    tipo_trabajo = answers.get("tipo_trabajo", "").lower().strip()

    if tipo_trabajo not in ["procedimiento", "proyecto"]:
        return {
            "valid": False,
            "missing": ["tipo_trabajo"],
            "tipo_trabajo": None
        }

    missing = []

    # Campos comunes
    if not answers.get("client"):
        missing.append("client")

    # Validar campos específicos del flujo
    if tipo_trabajo == "procedimiento":
        required_fields = [
            "jurisdiccion", "juzgado_num", "demarcacion", "num_procedimiento",
            "fecha_procedimiento", "parte_a", "parte_b", "materia_proc", "doc_type_proc"
        ]
        for field in required_fields:
            if not answers.get(field):
                missing.append(field)

    elif tipo_trabajo == "proyecto":
        required_fields = [
            "proyecto_year", "proyecto_month", "proyecto_nombre",
            "proyecto_materia", "doc_type_proyecto"
        ]
        for field in required_fields:
            if not answers.get(field):
                missing.append(field)

    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "tipo_trabajo": tipo_trabajo
    }
