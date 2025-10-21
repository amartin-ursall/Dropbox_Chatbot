"""
Path mapper para estructura de documentos legales
Sistema de organización implementado para URSALL Legal (la compañía/despacho)
Genera rutas de Dropbox con estructura organizacional profesional
"""
import re
from typing import Dict, Optional
from datetime import datetime
from app.validators import sanitize_filename_part


# Abreviaturas de jurisdicciones
JURISDICTION_MAP = {
    "contencioso": "CA",
    "contencioso-administrativo": "CA",
    "contencioso administrativo": "CA",
    "social": "SC",
    "laboral": "SC",
    "civil": "CIV",
    "penal": "PEN",
    "instruccion": "JPI",
    "instrucción": "JPI",
}

# Subcarpetas para Procedimientos Judiciales
PROCEDIMIENTO_SUBFOLDERS = [
    "01. Escritos presentados",
    "02. Resoluciones judiciales",
    "03. Pruebas",
    "03.1 Testifical",
    "03.2 Pericial",
    "03.3 Documental",
    "04. Doctrina y jurisprudencia",
    "05. Notificaciones del Juzgado",
    "06. Anotaciones internas",
    "07. Documentación del cliente",
    "08. Carpeta 0 – Almacenamiento rápido",
    "09. Agenda procesal y plazos",
    "10. Costas y gastos",
]

# Subcarpetas para Proyectos Jurídicos
PROYECTO_SUBFOLDERS = [
    "00. General",
    "01. Documentación recibida",
    "02. Borradores",
    "03. Documentación de estudio",
    "04. Comunicaciones",
    "05. Informe/Documento final",
    "06. Contratos o convenios asociados",
    "07. Anexos y notas adicionales",
]

# Mapeo de tipos de documento a subcarpetas de procedimiento
DOC_TYPE_TO_PROCEDIMIENTO_FOLDER = {
    "escrito": "01. Escritos presentados",
    "escritos": "01. Escritos presentados",
    "demanda": "01. Escritos presentados",
    "contestacion": "01. Escritos presentados",
    "contestación": "01. Escritos presentados",

    "sentencia": "02. Resoluciones judiciales",
    "auto": "02. Resoluciones judiciales",
    "resolucion": "02. Resoluciones judiciales",
    "resolución": "02. Resoluciones judiciales",
    "providencia": "02. Resoluciones judiciales",

    "testifical": "03.1 Testifical",
    "testimonio": "03.1 Testifical",

    "pericial": "03.2 Pericial",
    "peritaje": "03.2 Pericial",
    "informe pericial": "03.2 Pericial",

    "documental": "03.3 Documental",
    "documento": "03.3 Documental",
    "prueba documental": "03.3 Documental",

    "jurisprudencia": "04. Doctrina y jurisprudencia",
    "doctrina": "04. Doctrina y jurisprudencia",

    "notificacion": "05. Notificaciones del Juzgado",
    "notificación": "05. Notificaciones del Juzgado",
    "cedula": "05. Notificaciones del Juzgado",
    "cédula": "05. Notificaciones del Juzgado",

    "nota": "06. Anotaciones internas",
    "anotacion": "06. Anotaciones internas",
    "anotación": "06. Anotaciones internas",

    "costas": "10. Costas y gastos",
    "gastos": "10. Costas y gastos",
    "factura judicial": "10. Costas y gastos",
}

# Mapeo de tipos de documento a subcarpetas de proyecto
DOC_TYPE_TO_PROYECTO_FOLDER = {
    "informe": "05. Informe/Documento final",
    "dictamen": "05. Informe/Documento final",
    "documento final": "05. Informe/Documento final",

    "contrato": "06. Contratos o convenios asociados",
    "convenio": "06. Contratos o convenios asociados",

    "borrador": "02. Borradores",
    "draft": "02. Borradores",

    "comunicacion": "04. Comunicaciones",
    "comunicación": "04. Comunicaciones",
    "email": "04. Comunicaciones",
    "correo": "04. Comunicaciones",

    "documentacion": "01. Documentación recibida",
    "documentación": "01. Documentación recibida",
    "recibido": "01. Documentación recibida",
}


def build_procedimiento_name(
    year: str,
    month: str,
    jurisdiccion: str,
    juzgado_num: str,
    demarcacion: str,
    num_procedimiento: str,
    year_proc: str,
    parte_a: str,
    parte_b: str,
    materia: str
) -> str:
    """
    Construye el nombre del procedimiento judicial

    Formato: AAAA_MM_Juzgado_Demarcación_NºProcedimiento/AAAA_ParteA Vs ParteB_Materia

    Ejemplo: 2025_08_SC2_Tenerife_455/2025_Pedro Perez Vs Cabildo Gomera_Despidos

    Args:
        num_procedimiento: Número en formato "455/2025" - se extrae solo el número
    """
    # Obtener abreviatura de jurisdicción
    juris_abbr = JURISDICTION_MAP.get(jurisdiccion.lower(), jurisdiccion.upper()[:3])

    # Sanitizar nombres de partes
    parte_a_clean = sanitize_filename_part(parte_a)
    parte_b_clean = sanitize_filename_part(parte_b)
    materia_clean = sanitize_filename_part(materia)
    demarcacion_clean = sanitize_filename_part(demarcacion)

    # Extraer solo el número del procedimiento (antes de la barra)
    # Entrada: "455/2025" -> Salida: "455"
    solo_numero = num_procedimiento.split('/')[0] if '/' in num_procedimiento else num_procedimiento

    # Construir primera parte: AAAA_MM_Juzgado_Demarcación_NºProcedimiento
    primera_parte = f"{year}_{month}_{juris_abbr}{juzgado_num}_{demarcacion_clean}_{solo_numero}"

    # Construir segunda parte: AAAA_ParteA Vs ParteB_Materia
    segunda_parte = f"{year_proc}_{parte_a_clean} Vs {parte_b_clean}_{materia_clean}"

    return f"{primera_parte}/{segunda_parte}"


def build_proyecto_name(
    year: str,
    month: str,
    cliente: str,
    proyecto: str,
    materia: str
) -> str:
    """
    Construye el nombre del proyecto jurídico

    Formato: AAAA_MM_Cliente_Proyecto_Materia

    Ejemplo: 2025_06_AyuntamientoAdeje_Informe_SeguroSalud
    """
    return f"{year}_{month}_{cliente}_{proyecto}_{materia}"


def suggest_path_ursall(
    client_name: str,  # Cliente de URSALL Legal
    tipo_trabajo: str,  # "procedimiento" o "proyecto"
    doc_type: str = None,
    # Para procedimientos judiciales
    year: str = None,
    month: str = None,
    jurisdiccion: str = None,
    juzgado_num: str = None,
    demarcacion: str = None,
    num_procedimiento: str = None,
    year_proc: str = None,
    parte_a: str = None,
    parte_b: str = None,
    materia_proc: str = None,
    # Para proyectos jurídicos
    proyecto_nombre: str = None,
    materia_proyecto: str = None,
) -> Dict[str, any]:
    """
    Genera la ruta de Dropbox según la estructura URSALL Legal

    Args:
        client_name: Nombre del cliente (ej: "GRUPO GORETTI")
        tipo_trabajo: "procedimiento" o "proyecto"
        doc_type: Tipo de documento para determinar subcarpeta

        Para procedimientos judiciales:
        - year, month: Fecha del procedimiento (AAAA, MM)
        - jurisdiccion: Tipo de juzgado (contencioso, social, civil, penal, instrucción)
        - juzgado_num: Número del juzgado
        - demarcacion: Demarcación del juzgado
        - num_procedimiento: Número de procedimiento
        - year_proc: Año del procedimiento
        - parte_a, parte_b: Partes del procedimiento
        - materia_proc: Materia del procedimiento

        Para proyectos jurídicos:
        - year, month: Fecha del proyecto
        - proyecto_nombre: Nombre del proyecto
        - materia_proyecto: Materia del proyecto

    Returns:
        Dict con:
        - path: Ruta completa del folder
        - subfolder: Subcarpeta específica según tipo de documento
        - full_path: Ruta completa incluyendo subcarpeta
        - folder_structure: Lista de carpetas a crear
    """
    # Sanitizar nombre del cliente
    client_folder = sanitize_filename_part(client_name)

    if tipo_trabajo.lower() == "procedimiento":
        # Construir nombre del procedimiento
        if not all([year, month, jurisdiccion, juzgado_num, demarcacion,
                   num_procedimiento, year_proc, parte_a, parte_b, materia_proc]):
            raise ValueError("Faltan parámetros para construir el procedimiento judicial")

        procedimiento_name = build_procedimiento_name(
            year, month, jurisdiccion, juzgado_num, demarcacion,
            num_procedimiento, year_proc, parte_a, parte_b, materia_proc
        )

        # Ruta base
        base_path = f"/{client_folder}/1. Procedimientos Judiciales/{procedimiento_name}"

        # Determinar subcarpeta según tipo de documento
        subfolder = None
        if doc_type:
            doc_normalized = doc_type.lower().strip()
            subfolder = DOC_TYPE_TO_PROCEDIMIENTO_FOLDER.get(doc_normalized)

            # Si no hay mapeo directo, usar "Carpeta 0" por defecto
            if not subfolder:
                subfolder = "08. Carpeta 0 – Almacenamiento rápido"
        else:
            subfolder = "08. Carpeta 0 – Almacenamiento rápido"

        full_path = f"{base_path}/{subfolder}"

        # Estructura de carpetas a crear
        folder_structure = [
            f"/{client_folder}",
            f"/{client_folder}/1. Procedimientos Judiciales",
            base_path,
        ] + [f"{base_path}/{sf}" for sf in PROCEDIMIENTO_SUBFOLDERS]

        return {
            "path": base_path,
            "subfolder": subfolder,
            "full_path": full_path,
            "folder_structure": folder_structure,
            "tipo": "procedimiento"
        }

    elif tipo_trabajo.lower() == "proyecto":
        # Construir nombre del proyecto
        if not all([year, month, proyecto_nombre, materia_proyecto]):
            raise ValueError("Faltan parámetros para construir el proyecto jurídico")

        proyecto_name = build_proyecto_name(
            year, month, client_name, proyecto_nombre, materia_proyecto
        )

        # Ruta base
        base_path = f"/{client_folder}/2. Proyectos Jurídicos/{proyecto_name}"

        # Determinar subcarpeta según tipo de documento
        subfolder = None
        if doc_type:
            doc_normalized = doc_type.lower().strip()
            subfolder = DOC_TYPE_TO_PROYECTO_FOLDER.get(doc_normalized)

            # Si no hay mapeo directo, usar "General" por defecto
            if not subfolder:
                subfolder = "00. General"
        else:
            subfolder = "00. General"

        full_path = f"{base_path}/{subfolder}"

        # Estructura de carpetas a crear
        folder_structure = [
            f"/{client_folder}",
            f"/{client_folder}/2. Proyectos Jurídicos",
            base_path,
        ] + [f"{base_path}/{sf}" for sf in PROYECTO_SUBFOLDERS]

        return {
            "path": base_path,
            "subfolder": subfolder,
            "full_path": full_path,
            "folder_structure": folder_structure,
            "tipo": "proyecto"
        }

    else:
        raise ValueError(f"Tipo de trabajo inválido: {tipo_trabajo}. Debe ser 'procedimiento' o 'proyecto'")


def parse_procedimiento_input(user_input: str) -> Dict[str, str]:
    """
    Parsea la entrada del usuario para extraer datos de un procedimiento judicial

    Esta función intentaría extraer automáticamente los datos, pero es compleja.
    Por ahora, se usará un flujo de preguntas guiado.
    """
    # TODO: Implementar parsing inteligente si se necesita
    return {}
