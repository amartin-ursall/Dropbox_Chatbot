"""
File validation utilities
Refactored from main.py for better testability and separation of concerns
AD-2: Added date validation
AD-3: Added advanced semantic validation and suggestions
"""
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime, date, timedelta
import re

# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.jpg', '.jpeg', '.png', '.txt'}

# AD-3: Advanced validation constants
MAX_DOC_TYPE_LENGTH = 50
MAX_CLIENT_LENGTH = 100
OLD_DATE_WARNING_YEARS = 10


class FileValidationError(Exception):
    """Custom exception for file validation errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def validate_file_extension(filename: str) -> str:
    """
    Validate that file extension is allowed

    Args:
        filename: Original filename with extension

    Returns:
        Lowercase file extension (e.g., '.pdf')

    Raises:
        FileValidationError: If extension not in whitelist
    """
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"File extension '{extension}' not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            status_code=400
        )

    return extension


def validate_file_size(file_size: int) -> None:
    """
    Validate that file size is within limits

    Args:
        file_size: Size in bytes

    Raises:
        FileValidationError: If file exceeds MAX_FILE_SIZE
    """
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        raise FileValidationError(
            f"File size exceeds 50MB limit. Your file: {size_mb:.2f}MB",
            status_code=413
        )


def validate_upload_file(filename: str, file_size: int) -> Tuple[str, None]:
    """
    Complete validation for uploaded file

    Args:
        filename: Original filename
        file_size: Size in bytes

    Returns:
        Tuple of (extension, None) if valid

    Raises:
        FileValidationError: If validation fails
    """
    extension = validate_file_extension(filename)
    validate_file_size(file_size)
    return extension, None


def validate_text_answer(answer: str, min_length: int = 2) -> str:
    """
    Validate text answer for questions (doc_type, client)

    Args:
        answer: User's text answer
        min_length: Minimum required characters

    Returns:
        Stripped answer if valid

    Raises:
        FileValidationError: If answer is empty or too short
    """
    stripped = answer.strip()
    if len(stripped) < min_length:
        raise FileValidationError(
            f"La respuesta debe tener mínimo {min_length} caracteres",
            status_code=400
        )
    return stripped


def validate_date_format(date_str: str) -> str:
    """
    Validate date string in YYYY-MM-DD format

    Args:
        date_str: Date string to validate

    Returns:
        Valid date string

    Raises:
        FileValidationError: If format is invalid
    """
    # Check format with regex
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        raise FileValidationError(
            "Formato de fecha inválido. Usa YYYY-MM-DD (ejemplo: 2025-01-15)",
            status_code=400
        )

    # Validate it's a real date
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise FileValidationError(
            "Fecha inválida. Verifica el día y mes (ejemplo: 2025-01-15)",
            status_code=400
        )

    return date_str


def sanitize_filename_part(text: str) -> str:
    """
    Sanitize text for use in filename
    - Spaces → underscore
    - Remove special characters except _ and -
    - Remove accents

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text safe for filenames
    """
    import unicodedata

    # Normalize unicode (remove accents)
    normalized = unicodedata.normalize('NFKD', text)
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')

    # Replace spaces with underscores
    cleaned = ascii_text.replace(' ', '_')

    # Remove special chars except _ and -
    cleaned = re.sub(r'[^a-zA-Z0-9_-]', '', cleaned)

    return cleaned


# AD-3: Advanced validation functions

def validate_date_advanced(date_str: str) -> Tuple[str, Optional[str]]:
    """
    Advanced date validation with semantic checks

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Tuple of (validated_date, warning_message)
        Warning is None if no issues, string if old date

    Raises:
        FileValidationError: If date is invalid or in the future
    """
    # First validate format
    validated = validate_date_format(date_str)

    # Parse to date object
    parsed_date = datetime.strptime(validated, '%Y-%m-%d').date()
    today = date.today()

    # Check not in future
    if parsed_date > today:
        raise FileValidationError(
            "La fecha no puede estar en el futuro. Usa una fecha de hoy o anterior.",
            status_code=400
        )

    # Check if very old (>10 years) - warn but allow
    ten_years_ago = today - timedelta(days=365 * OLD_DATE_WARNING_YEARS)
    if parsed_date < ten_years_ago:
        warning = f"⚠️ La fecha es de hace más de {OLD_DATE_WARNING_YEARS} años. ¿Es correcto?"
        return validated, warning

    return validated, None


def validate_doc_type_advanced(doc_type: str) -> str:
    """
    Advanced document type validation
    - Only letters (a-z, A-Z) and spaces
    - Accents allowed
    - Min 2 chars, Max 50 chars

    Args:
        doc_type: Document type to validate

    Returns:
        Validated and stripped doc_type

    Raises:
        FileValidationError: If validation fails
    """
    stripped = doc_type.strip()

    # Check length
    if len(stripped) < 2:
        raise FileValidationError(
            "El tipo debe tener mínimo 2 caracteres",
            status_code=400
        )

    if len(stripped) > MAX_DOC_TYPE_LENGTH:
        raise FileValidationError(
            f"El tipo debe tener máximo {MAX_DOC_TYPE_LENGTH} caracteres",
            status_code=400
        )

    # Check only letters and spaces (allow accents)
    # Pattern: unicode letters (\p{L} equivalent) + spaces
    if not all(c.isalpha() or c.isspace() for c in stripped):
        raise FileValidationError(
            "El tipo debe contener solo letras y espacios (sin números ni símbolos). Ejemplo: Factura",
            status_code=400
        )

    return stripped


def validate_client_advanced(client: str) -> str:
    """
    Advanced client name validation
    - Letters, numbers, spaces, hyphens (-), dots (.)
    - Accents allowed
    - Min 2 chars, Max 100 chars

    Args:
        client: Client name to validate

    Returns:
        Validated and stripped client name

    Raises:
        FileValidationError: If validation fails
    """
    stripped = client.strip()

    # Check length
    if len(stripped) < 2:
        raise FileValidationError(
            "El cliente debe tener mínimo 2 caracteres",
            status_code=400
        )

    if len(stripped) > MAX_CLIENT_LENGTH:
        raise FileValidationError(
            f"El cliente debe tener máximo {MAX_CLIENT_LENGTH} caracteres",
            status_code=400
        )

    # Check allowed characters: letters, numbers, spaces, hyphens, dots
    # Reject: @, #, $, %, &, *, etc.
    # Allow unicode letters (including accents), numbers, spaces, dots, hyphens
    if not all(c.isalpha() or c.isdigit() or c.isspace() or c in '.-' for c in stripped):
        raise FileValidationError(
            "El cliente solo puede contener letras, números, espacios, guiones y puntos. Ejemplo: Acme Corp.",
            status_code=400
        )

    return stripped


def generate_doc_type_suggestion(invalid_input: str) -> Optional[str]:
    """
    Generate suggestion for invalid document type
    Removes numbers and special characters

    Args:
        invalid_input: Invalid doc type string

    Returns:
        Cleaned suggestion or None if can't generate
    """
    # Remove numbers and special characters, keep only letters and spaces
    cleaned = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]', '', invalid_input)
    cleaned = cleaned.strip()

    # Only return if result has at least 2 chars
    if len(cleaned) >= 2:
        return cleaned

    return None


def generate_date_suggestion(invalid_input: str) -> Optional[str]:
    """
    Generate suggestion for common date format mistakes

    Tries to parse:
    - DD-MM-YYYY → YYYY-MM-DD
    - MM/DD/YYYY → YYYY-MM-DD
    - DD/MM/YYYY → YYYY-MM-DD

    Args:
        invalid_input: Invalid date string

    Returns:
        Suggested date in YYYY-MM-DD format or None
    """
    # Try DD-MM-YYYY
    match = re.match(r'^(\d{2})-(\d{2})-(\d{4})$', invalid_input)
    if match:
        day, month, year = match.groups()
        try:
            # Validate it's a real date
            datetime(int(year), int(month), int(day))
            return f"{year}-{month}-{day}"
        except ValueError:
            pass

    # Try MM/DD/YYYY
    match = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', invalid_input)
    if match:
        month, day, year = match.groups()
        try:
            datetime(int(year), int(month), int(day))
            return f"{year}-{month}-{day}"
        except ValueError:
            pass

    # Try DD/MM/YYYY (European format)
    match = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', invalid_input)
    if match:
        day, month, year = match.groups()
        try:
            datetime(int(year), int(month), int(day))
            return f"{year}-{month}-{day}"
        except ValueError:
            pass

    return None
