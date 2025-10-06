"""
Question flow logic for URSALL Legal structure
Maneja dos flujos: Procedimientos Judiciales y Proyectos Jurídicos
"""
from typing import Dict, Optional


# Definición de flujos de preguntas para URSALL
QUESTIONS_URSALL = {
    # Pregunta inicial: determinar tipo de trabajo
    "tipo_trabajo": {
        "question_id": "tipo_trabajo",
        "question_text": "¿Es un Procedimiento Judicial o un Proyecto Jurídico? (escribe: procedimiento o proyecto)",
        "required": True,
        "validation": {"type": "choice", "choices": ["procedimiento", "proyecto"]},
        "next": "client"
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
        }
    },

    # ============= FLUJO PROCEDIMIENTO JUDICIAL =============

    "jurisdiccion": {
        "question_id": "jurisdiccion",
        "question_text": "¿Qué tipo de juzgado es? (contencioso, social, civil, penal, instrucción)",
        "required": True,
        "validation": {"type": "choice", "choices": ["contencioso", "social", "civil", "penal", "instrucción", "instruccion"]},
        "next": "juzgado_num",
        "flow": "procedimiento"
    },

    "juzgado_num": {
        "question_id": "juzgado_num",
        "question_text": "¿Número del juzgado? (ej: 1, 2, 3)",
        "required": True,
        "validation": {"type": "number"},
        "next": "demarcacion",
        "flow": "procedimiento"
    },

    "demarcacion": {
        "question_id": "demarcacion",
        "question_text": "¿Demarcación del juzgado? (ej: Santa Cruz, Tenerife, La Gomera)",
        "required": True,
        "validation": {"min_length": 2},
        "next": "num_procedimiento",
        "flow": "procedimiento"
    },

    "num_procedimiento": {
        "question_id": "num_procedimiento",
        "question_text": "¿Número de procedimiento/autos? (ej: 455/2025, 245/2025)",
        "required": True,
        "validation": {"pattern": r"^\d+/\d{4}$"},
        "next": "fecha_procedimiento",
        "flow": "procedimiento"
    },

    "fecha_procedimiento": {
        "question_id": "fecha_procedimiento",
        "question_text": "¿Fecha del procedimiento? (formato: YYYY-MM-DD)",
        "required": True,
        "validation": {"format": "date"},
        "next": "parte_a",
        "flow": "procedimiento"
    },

    "parte_a": {
        "question_id": "parte_a",
        "question_text": "¿Nombre de la parte actora/demandante? (ej: Pedro Perez, Ministerio Fiscal)",
        "required": True,
        "validation": {"min_length": 2},
        "next": "parte_b",
        "flow": "procedimiento"
    },

    "parte_b": {
        "question_id": "parte_b",
        "question_text": "¿Nombre de la parte demandada? (ej: Cabildo Gomera, Motor 7 Islas)",
        "required": True,
        "validation": {"min_length": 2},
        "next": "materia_proc",
        "flow": "procedimiento"
    },

    "materia_proc": {
        "question_id": "materia_proc",
        "question_text": "¿Materia del procedimiento? (ej: Despidos, Fijeza, Urbanismo, Art316CP)",
        "required": True,
        "validation": {"min_length": 2},
        "next": "doc_type_proc",
        "flow": "procedimiento"
    },

    "doc_type_proc": {
        "question_id": "doc_type_proc",
        "question_text": "¿Tipo de documento? (ej: Escrito, Sentencia, Pericial, Notificación)",
        "required": True,
        "validation": {"min_length": 2},
        "next": None,  # Última pregunta del flujo procedimiento
        "flow": "procedimiento"
    },

    # ============= FLUJO PROYECTO JURÍDICO =============

    "proyecto_year": {
        "question_id": "proyecto_year",
        "question_text": "¿Año del proyecto? (formato: YYYY)",
        "required": True,
        "validation": {"pattern": r"^\d{4}$"},
        "next": "proyecto_month",
        "flow": "proyecto"
    },

    "proyecto_month": {
        "question_id": "proyecto_month",
        "question_text": "¿Mes del proyecto? (formato: MM, ej: 01, 06, 12)",
        "required": True,
        "validation": {"pattern": r"^(0[1-9]|1[0-2])$"},
        "next": "proyecto_nombre",
        "flow": "proyecto"
    },

    "proyecto_nombre": {
        "question_id": "proyecto_nombre",
        "question_text": "¿Nombre del proyecto? (ej: Informe, Dictamen, Estudio)",
        "required": True,
        "validation": {"min_length": 2},
        "next": "proyecto_materia",
        "flow": "proyecto"
    },

    "proyecto_materia": {
        "question_id": "proyecto_materia",
        "question_text": "¿Materia del proyecto? (ej: Seguro Salud, Urbanismo, Laboral)",
        "required": True,
        "validation": {"min_length": 2},
        "next": "doc_type_proyecto",
        "flow": "proyecto"
    },

    "doc_type_proyecto": {
        "question_id": "doc_type_proyecto",
        "question_text": "¿Tipo de documento? (ej: Informe, Borrador, Contrato, Comunicación)",
        "required": True,
        "validation": {"min_length": 2},
        "next": None,  # Última pregunta del flujo proyecto
        "flow": "proyecto"
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
