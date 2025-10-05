"""
Path mapper module - AD-4
Maps document types to Dropbox folder paths
"""
import unicodedata


# Path mapping - case insensitive
PATH_MAP = {
    "factura": "/Documentos/Facturas",
    "facturas": "/Documentos/Facturas",
    "contrato": "/Documentos/Contratos",
    "contratos": "/Documentos/Contratos",
    "recibo": "/Documentos/Recibos",
    "recibos": "/Documentos/Recibos",
    "nomina": "/Documentos/Nóminas",
    "nómina": "/Documentos/Nóminas",
    "nominas": "/Documentos/Nóminas",
    "nóminas": "/Documentos/Nóminas",
    "presupuesto": "/Documentos/Presupuestos",
    "presupuestos": "/Documentos/Presupuestos",
}

DEFAULT_PATH = "/Documentos/Otros"


def normalize_doc_type(doc_type: str) -> str:
    """
    Normalize document type for mapping
    - Convert to lowercase
    - Handle accents (NFD normalization)
    """
    # Lowercase
    normalized = doc_type.lower().strip()
    return normalized


def suggest_path(doc_type: str) -> str:
    """
    Suggest Dropbox path based on document type

    Args:
        doc_type: Document type (e.g., "Factura", "Contrato")

    Returns:
        Suggested Dropbox path (e.g., "/Documentos/Facturas")
    """
    normalized = normalize_doc_type(doc_type)

    # Try exact match first
    if normalized in PATH_MAP:
        return PATH_MAP[normalized]

    # Try without accents
    normalized_no_accents = (
        unicodedata.normalize('NFD', normalized)
        .encode('ascii', 'ignore')
        .decode('utf-8')
    )
    if normalized_no_accents in PATH_MAP:
        return PATH_MAP[normalized_no_accents]

    # Default to Otros
    return DEFAULT_PATH


def get_full_path(path: str, filename: str) -> str:
    """
    Combine path and filename to get full Dropbox path

    Args:
        path: Dropbox folder path (e.g., "/Documentos/Facturas")
        filename: File name (e.g., "2025-01-15_Factura_Cliente.pdf")

    Returns:
        Full path (e.g., "/Documentos/Facturas/2025-01-15_Factura_Cliente.pdf")
    """
    return f"{path}/{filename}"
