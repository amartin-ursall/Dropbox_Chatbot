"""
Path mapper module - AD-4
Maps document types to Dropbox folder paths with intelligent categorization
"""
import unicodedata
import re
from datetime import datetime
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


# Enhanced path mapping with more categories
PATH_MAP = {
    # Documentos fiscales y contables
    "factura": "/Documentos/Facturas",
    "facturas": "/Documentos/Facturas",
    "recibo": "/Documentos/Recibos",
    "recibos": "/Documentos/Recibos",
    "ticket": "/Documentos/Recibos",
    "tickets": "/Documentos/Recibos",

    # Nóminas y RRHH
    "nomina": "/Documentos/Nóminas",
    "nómina": "/Documentos/Nóminas",
    "nominas": "/Documentos/Nóminas",
    "nóminas": "/Documentos/Nóminas",

    # Comerciales
    "presupuesto": "/Documentos/Presupuestos",
    "presupuestos": "/Documentos/Presupuestos",
    "pedido": "/Documentos/Pedidos",
    "pedidos": "/Documentos/Pedidos",
    "albaran": "/Documentos/Albaranes",
    "albarán": "/Documentos/Albaranes",
    "albaranes": "/Documentos/Albaranes",

    # Legales
    "contrato": "/Documentos/Contratos",
    "contratos": "/Documentos/Contratos",
    "juridico": "/Documentos/Legal",
    "jurídico": "/Documentos/Legal",
    "legal": "/Documentos/Legal",
    "escritura": "/Documentos/Legal",
    "escrituras": "/Documentos/Legal",
    "certificado": "/Documentos/Certificados",
    "certificados": "/Documentos/Certificados",

    # Otros
    "nota": "/Documentos/Notas",
    "notas": "/Documentos/Notas",
    "informe": "/Documentos/Informes",
    "informes": "/Documentos/Informes",
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


def suggest_path(doc_type: str, client: str = None, date: str = None) -> str:
    """
    Suggest Dropbox path based on document type with optional sub-organization

    Args:
        doc_type: Document type (e.g., "Factura", "Contrato")
        client: Client name (optional, for client-based organization)
        date: Date string in YYYY-MM-DD format (optional, for year-based organization)

    Returns:
        Suggested Dropbox path with intelligent organization
        Examples:
        - "/Documentos/Facturas/2025/Acme_Corp"
        - "/Documentos/Contratos/2025"
        - "/Documentos/Legal/Acme_Corp"
    """
    normalized = normalize_doc_type(doc_type)

    # Try exact match first
    base_path = None
    if normalized in PATH_MAP:
        base_path = PATH_MAP[normalized]
    else:
        # Try without accents
        normalized_no_accents = (
            unicodedata.normalize('NFD', normalized)
            .encode('ascii', 'ignore')
            .decode('utf-8')
        )
        if normalized_no_accents in PATH_MAP:
            base_path = PATH_MAP[normalized_no_accents]
        else:
            base_path = DEFAULT_PATH

    # Add intelligent sub-organization
    # For certain document types, organize by year and/or client
    organize_by_year = normalized in [
        "factura", "facturas", "recibo", "recibos",
        "nomina", "nómina", "nominas", "nóminas",
        "presupuesto", "presupuestos"
    ]

    organize_by_client = normalized in [
        "factura", "facturas", "contrato", "contratos",
        "presupuesto", "presupuestos", "juridico", "jurídico", "legal"
    ]

    # Build enhanced path
    path_parts = [base_path]

    # Add year subfolder if applicable
    if organize_by_year and date:
        try:
            year = date.split('-')[0]  # Extract year from YYYY-MM-DD
            path_parts.append(year)
        except:
            pass

    # Add client subfolder if applicable and provided
    if organize_by_client and client:
        # Sanitize client name for folder
        from app.validators import sanitize_filename_part
        client_folder = sanitize_filename_part(client)
        path_parts.append(client_folder)

    return "/".join(path_parts)


def suggest_path_intelligent(
    doc_type: str,
    client: str,
    date: str,
    dropbox_structure: Dict[str, List[str]] = None
) -> Dict[str, any]:
    """
    Intelligently suggest Dropbox path based on existing folder structure

    Args:
        doc_type: Document type extracted by Gemini
        client: Client name extracted by Gemini
        date: Date in YYYY-MM-DD format
        dropbox_structure: Existing folder structure from Dropbox

    Returns:
        Dict with:
        - path: Suggested path
        - matched_existing: Whether it matched existing folders
        - created_folders: Folders that would need to be created
    """
    from app.validators import sanitize_filename_part

    normalized_type = normalize_doc_type(doc_type)

    # Get base path
    base_path = PATH_MAP.get(normalized_type)
    if not base_path:
        normalized_no_accents = (
            unicodedata.normalize('NFD', normalized_type)
            .encode('ascii', 'ignore')
            .decode('utf-8')
        )
        base_path = PATH_MAP.get(normalized_no_accents, DEFAULT_PATH)

    # Extract year from date
    try:
        year = date.split('-')[0]
    except:
        year = None

    # Sanitize client name
    client_sanitized = sanitize_filename_part(client) if client else None

    # Decision tree based on document type and existing structure
    path_parts = [base_path]
    matched_existing = False
    created_folders = []

    if dropbox_structure:
        # Check if base path exists
        if base_path in dropbox_structure:
            existing_subfolders = dropbox_structure[base_path]

            # Strategy 1: Check if year folder exists
            if year and year in existing_subfolders:
                path_parts.append(year)
                matched_existing = True

                # Check if this year folder has client subfolders
                year_path = f"{base_path}/{year}"
                if year_path in dropbox_structure:
                    year_subfolders = dropbox_structure[year_path]

                    # Check if client folder exists
                    if client_sanitized and client_sanitized in year_subfolders:
                        path_parts.append(client_sanitized)
                    elif client_sanitized:
                        # Year exists but not client - create client subfolder
                        path_parts.append(client_sanitized)
                        created_folders.append(f"{year_path}/{client_sanitized}")

            # Strategy 2: Check if client folder exists at base level
            elif client_sanitized and client_sanitized in existing_subfolders:
                path_parts.append(client_sanitized)
                matched_existing = True

            # Strategy 3: Use existing structure pattern OR create with client subfolder
            elif existing_subfolders:
                # Analyze existing pattern
                has_years = any(f.isdigit() and len(f) == 4 for f in existing_subfolders)
                has_clients = any(not f.isdigit() for f in existing_subfolders)

                if has_years and year:
                    # Follow year-based organization
                    path_parts.append(year)
                    created_folders.append(f"{base_path}/{year}")

                    # ALWAYS add client subfolder for better organization
                    if client_sanitized:
                        path_parts.append(client_sanitized)
                        created_folders.append(f"{base_path}/{year}/{client_sanitized}")

                elif has_clients and client_sanitized:
                    # Follow client-based organization
                    path_parts.append(client_sanitized)
                    created_folders.append(f"{base_path}/{client_sanitized}")

            # Strategy 4: No existing subfolders - create structure with client
            else:
                # Create organized structure based on document type
                if normalized_type in ["factura", "facturas", "recibo", "recibos", "nomina", "nómina", "presupuesto", "presupuestos"]:
                    # Year-based organization with client subfolder
                    if year:
                        path_parts.append(year)
                        created_folders.append(f"{base_path}/{year}")
                    if client_sanitized:
                        path_parts.append(client_sanitized)
                        if year:
                            created_folders.append(f"{base_path}/{year}/{client_sanitized}")
                        else:
                            created_folders.append(f"{base_path}/{client_sanitized}")
                else:
                    # Client-based for other documents
                    if client_sanitized:
                        path_parts.append(client_sanitized)
                        created_folders.append(f"{base_path}/{client_sanitized}")

        else:
            # Base path doesn't exist - create default structure
            if normalized_type in ["factura", "facturas", "recibo", "recibos", "nomina", "nómina"]:
                # Year-based for recurring docs
                if year:
                    path_parts.append(year)
                    created_folders.append(f"{base_path}/{year}")
                if client_sanitized:
                    path_parts.append(client_sanitized)
                    created_folders.append(f"{base_path}/{year}/{client_sanitized}")

            elif normalized_type in ["contrato", "contratos", "juridico", "jurídico", "legal"]:
                # Client-based for important docs
                if client_sanitized:
                    path_parts.append(client_sanitized)
                    created_folders.append(f"{base_path}/{client_sanitized}")

    else:
        # No structure provided - use default logic with client subfolders
        if normalized_type in ["factura", "facturas", "recibo", "recibos", "nomina", "nómina", "presupuesto", "presupuestos"]:
            # Year-based organization with client subfolder
            if year:
                path_parts.append(year)
            # ALWAYS add client subfolder when provided
            if client_sanitized:
                path_parts.append(client_sanitized)
        elif normalized_type in ["contrato", "contratos", "juridico", "jurídico", "legal"]:
            # Client-based for important docs
            if client_sanitized:
                path_parts.append(client_sanitized)
        else:
            # For other document types, still organize by client if provided
            if client_sanitized:
                path_parts.append(client_sanitized)

    final_path = "/".join(path_parts)

    return {
        "path": final_path,
        "matched_existing": matched_existing,
        "created_folders": created_folders,
        "base_path": base_path,
        "organization": {
            "year": year if year in path_parts else None,
            "client": client_sanitized if client_sanitized in path_parts else None
        }
    }


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
