"""
NLP Extractor - Intelligent information extraction
Extracts key information from user responses instead of taking them literally
"""
import re
from typing import Optional, List
from datetime import datetime


# Common patterns for each type of information
CLIENT_PATTERNS = [
    r'(?:cliente|nombre|empresa|compañía|se llama|llamado?a?)\s+(?:es|:)?\s*([A-ZÁÉÍÓÚa-záéíóúñü][A-ZÁÉÍÓÚa-záéíóúñü\s\.\-&,]+)',
    r'^([A-ZÁÉÍÓÚa-záéíóúñü][A-ZÁÉÍÓÚa-záéíóúñü\s\.\-&,]+)$',  # Just the name
]

DOC_TYPE_PATTERNS = [
    r'(?:tipo|documento|es|tipo de documento)\s+(?:es|:)?\s*(?:un?a?)\s*([A-ZÁÉÍÓÚa-záéíóúñü]+(?:\s+[A-ZÁÉÍÓÚa-záéíóúñü]+)?)',
    r'(?:es|son)\s+(?:un?a?s?)\s+([A-ZÁÉÍÓÚa-záéíóúñü]+(?:\s+[A-ZÁÉÍÓÚa-záéíóúñü]+)?)',
    r'^(?:un?a?s?)\s+([A-ZÁÉÍÓÚa-záéíóúñü]+(?:\s+[A-ZÁÉÍÓÚa-záéíóúñü]+)?)$',  # "una factura", "un contrato"
    r'^([A-ZÁÉÍÓÚa-záéíóúñü]+(?:\s+[A-ZÁÉÍÓÚa-záéíóúñü]+)?)$',  # Just the type
]

DATE_PATTERNS = [
    r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
    r'(\d{2}/\d{2}/\d{4})',  # DD/MM/YYYY or MM/DD/YYYY
    r'(\d{2}-\d{2}-\d{4})',  # DD-MM-YYYY
    r'(?:fecha|date|día)\s+(?:es|:)?\s*(\d{4}-\d{2}-\d{2})',
    r'(?:fecha|date|día)\s+(?:es|:)?\s*(\d{2}/\d{2}/\d{4})',
]

# Known document types for smart matching
KNOWN_DOC_TYPES = [
    'factura', 'facturas', 'contrato', 'contratos', 'recibo', 'recibos',
    'nómina', 'nomina', 'nóminas', 'nominas', 'presupuesto', 'presupuestos',
    'albarán', 'albaran', 'albaranes', 'pedido', 'pedidos', 'nota', 'notas'
]


def extract_client_name(user_input: str) -> str:
    """
    Extract client name from user response

    Examples:
    - "El cliente es Acme Corp" → "Acme Corp"
    - "El nombre del cliente es Juan Pérez" → "Juan Pérez"
    - "Acme Corp" → "Acme Corp"
    - "se llama Microsoft España S.L." → "Microsoft España S.L."

    Args:
        user_input: Raw user response

    Returns:
        Extracted client name
    """
    user_input = user_input.strip()

    # Try patterns
    for pattern in CLIENT_PATTERNS:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            extracted = match.group(1).strip()
            # Clean up common trailing words
            extracted = re.sub(r'\s+(es|son|fue|era)$', '', extracted, flags=re.IGNORECASE)
            return extracted

    # If no pattern matches, try to clean the input
    # Remove common prefix words
    cleaned = re.sub(
        r'^(el\s+cliente\s+es|el\s+nombre\s+es|se\s+llama|llamado?a?|empresa|compañía|cliente)\s*:?\s*',
        '',
        user_input,
        flags=re.IGNORECASE
    )
    cleaned = cleaned.strip()

    # If we got something reasonable, return it
    if len(cleaned) >= 2 and not cleaned.lower().startswith(('el ', 'la ', 'los ', 'las ')):
        return cleaned

    # Last resort: return original input (will be validated later)
    return user_input


def extract_doc_type(user_input: str) -> str:
    """
    Extract document type from user response

    Examples:
    - "Es una factura" → "factura"
    - "El tipo de documento es un contrato" → "contrato"
    - "Factura" → "Factura"
    - "son presupuestos" → "presupuestos"

    Args:
        user_input: Raw user response

    Returns:
        Extracted document type
    """
    user_input = user_input.strip()

    # Try patterns
    for pattern in DOC_TYPE_PATTERNS:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            extracted = match.group(1).strip()
            # Check if it's a known doc type
            if extracted.lower() in KNOWN_DOC_TYPES:
                return extracted
            # If not known but looks reasonable, return it
            if len(extracted) >= 2 and extracted.replace(' ', '').isalpha():
                return extracted

    # Try to find any known doc type in the input
    words = user_input.lower().split()
    for word in words:
        if word in KNOWN_DOC_TYPES:
            return word

    # Clean the input from common prefixes
    cleaned = re.sub(
        r'^(es\s+un?a?|tipo\s+de\s+documento|documento|tipo)\s*:?\s*',
        '',
        user_input,
        flags=re.IGNORECASE
    )
    cleaned = cleaned.strip()

    # Remove articles at the beginning
    cleaned = re.sub(r'^(un?a?s?)\s+', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()

    # If we got something reasonable, return it
    if len(cleaned) >= 2 and cleaned.replace(' ', '').isalpha():
        return cleaned

    # Last resort: return original input (will be validated later)
    return user_input


def extract_date(user_input: str) -> str:
    """
    Extract date from user response

    Examples:
    - "La fecha es 2025-01-15" → "2025-01-15"
    - "2025-01-15" → "2025-01-15"
    - "15/01/2025" → "2025-01-15"
    - "Es del día 15-01-2025" → "2025-01-15"

    Args:
        user_input: Raw user response

    Returns:
        Extracted date (converted to YYYY-MM-DD if possible)
    """
    user_input = user_input.strip()

    # Try patterns
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, user_input)
        if match:
            date_str = match.group(1)
            # Try to normalize to YYYY-MM-DD
            return normalize_date_format(date_str)

    # If no pattern matches but input looks like a date, try to parse it
    if re.match(r'^\d{2,4}[-/]\d{2}[-/]\d{2,4}$', user_input):
        return normalize_date_format(user_input)

    # Last resort: return original input (will be validated later)
    return user_input


def normalize_date_format(date_str: str) -> str:
    """
    Try to convert various date formats to YYYY-MM-DD

    Args:
        date_str: Date in various formats

    Returns:
        Date in YYYY-MM-DD format if possible, otherwise original
    """
    # Already in correct format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str

    # DD/MM/YYYY → YYYY-MM-DD
    match = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', date_str)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month}-{day}"

    # DD-MM-YYYY → YYYY-MM-DD
    match = re.match(r'^(\d{2})-(\d{2})-(\d{4})$', date_str)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month}-{day}"

    # MM/DD/YYYY (less common, risky)
    # We'll skip this to avoid confusion

    return date_str


def extract_information(question_id: str, user_input: str) -> str:
    """
    Main extraction function - routes to appropriate extractor

    Args:
        question_id: Type of question (doc_type, client, date)
        user_input: Raw user response

    Returns:
        Extracted information
    """
    if question_id == "client":
        return extract_client_name(user_input)
    elif question_id == "doc_type":
        return extract_doc_type(user_input)
    elif question_id == "date":
        return extract_date(user_input)
    else:
        return user_input.strip()
