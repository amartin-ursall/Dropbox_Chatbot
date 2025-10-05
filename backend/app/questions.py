"""
Question flow logic - AD-2
Extracted from main.py for better testability and organization
"""
from typing import Dict, Optional


# Question definitions
QUESTIONS = {
    "doc_type": {
        "question_id": "doc_type",
        "question_text": "¿Qué tipo de documento es? (ej: Factura, Contrato, Presupuesto)",
        "required": True,
        "validation": {"min_length": 2, "only_letters": True},  # AD-3
        "next": "client"
    },
    "client": {
        "question_id": "client",
        "question_text": "¿Cuál es el nombre del cliente?",
        "required": True,
        "validation": {"min_length": 2},
        "next": "date"
    },
    "date": {
        "question_id": "date",
        "question_text": "¿Cuál es la fecha del documento? (formato: YYYY-MM-DD)",
        "required": True,
        "validation": {"format": "YYYY-MM-DD"},
        "next": None  # Last question
    }
}


def get_first_question() -> Dict:
    """Get the first question in the flow"""
    question = QUESTIONS["doc_type"].copy()
    question.pop("next", None)  # Don't expose 'next' to client
    return question


def get_next_question(current_question_id: str) -> Optional[Dict]:
    """
    Get next question after current one

    Args:
        current_question_id: ID of the question just answered

    Returns:
        Next question dict or None if completed
    """
    current = QUESTIONS.get(current_question_id)
    if not current:
        return None

    next_id = current.get("next")
    if not next_id:
        return None

    next_question = QUESTIONS[next_id].copy()
    next_question.pop("next", None)  # Don't expose 'next' to client
    return next_question


def is_last_question(question_id: str) -> bool:
    """Check if this is the last question in the flow"""
    question = QUESTIONS.get(question_id)
    return question is not None and question.get("next") is None
