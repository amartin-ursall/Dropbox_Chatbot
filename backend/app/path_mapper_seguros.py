"""
Path mapper para estructura de Seguros
Genera rutas de Dropbox para documentos de seguros
"""
from typing import Dict
from app.validators import sanitize_filename_part


def suggest_path_seguros(
    compania: str,
    tomador: str,
    ramo: str,
    tipo_seguro: str,
    fecha: str,
    doc_type: str
) -> Dict[str, any]:
    """
    Genera la ruta de Dropbox para documentos de seguros

    Estructura propuesta:
    /Seguros/[Compañía]/[Ramo]/[Tomador]/[Año]/[Tipo_Documento]/

    Args:
        compania: Nombre de la compañía aseguradora
        tomador: Nombre del tomador del seguro
        ramo: Tipo de seguro (salud, auto, hogar, etc.)
        tipo_seguro: Tipo de documento (poliza, siniestro, comunicacion, otro)
        fecha: Fecha del documento (YYYY-MM-DD)
        doc_type: Descripción específica del documento

    Returns:
        Dict con path, subfolder, full_path y folder_structure
    """
    # Sanitizar nombres
    compania_clean = sanitize_filename_part(compania)
    tomador_clean = sanitize_filename_part(tomador)
    ramo_clean = sanitize_filename_part(ramo)
    tipo_seguro_clean = sanitize_filename_part(tipo_seguro)
    doc_type_clean = sanitize_filename_part(doc_type)

    # Extraer año de la fecha
    year = fecha.split("-")[0]

    # Mapear tipo_seguro a carpeta
    tipo_folder_map = {
        "poliza": "01. Pólizas",
        "siniestro": "02. Siniestros",
        "comunicacion": "03. Comunicaciones",
        "otro": "04. Otros"
    }

    tipo_folder = tipo_folder_map.get(tipo_seguro.lower(), "04. Otros")

    # Construir ruta base
    base_path = f"/Seguros/{compania_clean}/{ramo_clean}/{tomador_clean}/{year}"

    # Subcarpeta según tipo
    subfolder = tipo_folder
    full_path = f"{base_path}/{subfolder}"

    # Estructura de carpetas a crear
    folder_structure = [
        "/Seguros",
        f"/Seguros/{compania_clean}",
        f"/Seguros/{compania_clean}/{ramo_clean}",
        f"/Seguros/{compania_clean}/{ramo_clean}/{tomador_clean}",
        base_path,
        f"{base_path}/01. Pólizas",
        f"{base_path}/02. Siniestros",
        f"{base_path}/03. Comunicaciones",
        f"{base_path}/04. Otros",
    ]

    return {
        "path": base_path,
        "subfolder": subfolder,
        "full_path": full_path,
        "folder_structure": folder_structure,
        "tipo": "seguros"
    }
