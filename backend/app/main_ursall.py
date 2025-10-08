"""
Endpoints para el flujo URSALL Legal
Maneja procedimientos judiciales y proyectos jurídicos
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import logging

from app.questions_ursall import (
    get_first_question_ursall,
    get_next_question_ursall,
    is_last_question_ursall,
    validate_ursall_answers
)
from app.nlp_extractor_legal import extract_information_legal
from app.path_mapper_ursall import suggest_path_ursall
from app.validators import sanitize_filename_part
from app import auth
from app.dropbox_uploader import upload_file_to_dropbox

logger = logging.getLogger(__name__)

# Router para endpoints URSALL
router = APIRouter(prefix="/api/ursall", tags=["URSALL"])

# Almacenamiento de sesiones (en producción, usar base de datos)
ursall_sessions: Dict[str, Dict] = {}


# Modelos Pydantic
class URSALLQuestionStart(BaseModel):
    file_id: str


class URSALLQuestionAnswer(BaseModel):
    file_id: str
    question_id: str
    answer: str


class URSALLGeneratePath(BaseModel):
    file_id: str
    answers: Dict[str, str]
    original_extension: str


class URSALLUploadFinal(BaseModel):
    file_id: str
    filename: str
    dropbox_path: str
    folder_structure: list


@router.post("/questions/start")
async def start_ursall_questions(payload: URSALLQuestionStart) -> Dict:
    """
    Iniciar flujo de preguntas URSALL
    Retorna la primera pregunta (tipo_trabajo)
    """
    file_id = payload.file_id

    # Inicializar sesión
    ursall_sessions[file_id] = {
        "current_question": "tipo_trabajo",
        "answers": {},
        "extracted_answers": {}
    }

    return get_first_question_ursall()


@router.post("/questions/answer")
async def answer_ursall_question(payload: URSALLQuestionAnswer) -> Dict:
    """
    Responder una pregunta del flujo URSALL
    Extrae información usando NLP legal y valida
    """
    file_id = payload.file_id
    question_id = payload.question_id
    answer = payload.answer

    # Verificar sesión
    if file_id not in ursall_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    session = ursall_sessions[file_id]

    # PASO 1: Extraer información usando NLP legal
    logger.info(f"Respuesta original: {answer}")

    try:
        extracted_answer = extract_information_legal(question_id, answer)
        logger.info(f"Información extraída: {extracted_answer}")
    except Exception as e:
        logger.error(f"Error en extracción NLP: {e}")
        extracted_answer = answer.strip()

    # PASO 2: Validaciones básicas con mensajes de error claros
    if not extracted_answer:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "respuesta_vacia",
                "message": "La respuesta no puede estar vacía. Por favor, proporciona una respuesta.",
                "field": question_id
            }
        )
    
    if isinstance(extracted_answer, str) and len(extracted_answer.strip()) < 1:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "respuesta_invalida",
                "message": "La respuesta proporcionada no es válida. Por favor, intenta nuevamente.",
                "field": question_id
            }
        )

    # PASO 3: Validaciones específicas por tipo de pregunta con mensajes claros
    if question_id == "tipo_trabajo":
        if extracted_answer.lower() not in ["procedimiento", "proyecto"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "tipo_trabajo_invalido",
                    "message": "El tipo de trabajo debe ser 'procedimiento' o 'proyecto'. Por favor, selecciona una opción válida.",
                    "field": question_id,
                    "valid_options": ["procedimiento", "proyecto"]
                }
            )
        extracted_answer = extracted_answer.lower()

    elif question_id == "num_procedimiento":
        # Validar formato XXX/YYYY
        import re
        if not re.match(r'^\d+/\d{4}$', str(extracted_answer)):
            raise HTTPException(
                status_code=400,
                detail="Formato inválido. Debe ser XXX/YYYY (ej: 455/2025)"
            )

    elif question_id in ["proyecto_year", "fecha_procedimiento"]:
        # Validar año o fecha
        import re
        if question_id == "proyecto_year":
            if not re.match(r'^\d{4}$', str(extracted_answer)):
                raise HTTPException(
                    status_code=400,
                    detail="Año inválido. Debe ser YYYY (ej: 2025)"
                )
        else:
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(extracted_answer)):
                raise HTTPException(
                    status_code=400,
                    detail="Fecha inválida. Debe ser YYYY-MM-DD (ej: 2025-01-15)"
                )

    elif question_id == "proyecto_month":
        import re
        if not re.match(r'^(0[1-9]|1[0-2])$', str(extracted_answer)):
            raise HTTPException(
                status_code=400,
                detail="Mes inválido. Debe ser MM (ej: 01, 06, 12)"
            )

    # PASO 4: Almacenar respuesta
    session["answers"][question_id] = extracted_answer
    session["extracted_answers"][question_id] = extracted_answer

    # PASO 5: Obtener siguiente pregunta
    next_q = get_next_question_ursall(question_id, session["answers"])
    completed = is_last_question_ursall(question_id)

    # PASO 6: Si es "partes", necesitamos extraer parte_a y parte_b
    if question_id == "partes":
        logger.info(f"Procesando campo 'partes': {extracted_answer}")

        # Si el extractor ya devolvió un diccionario con las partes
        if isinstance(extracted_answer, dict):
            parte_a = extracted_answer.get("parte_a", "")
            parte_b = extracted_answer.get("parte_b", "")
            logger.info(f"Extractor devolvió partes - parte_a: {parte_a}, parte_b: {parte_b}")
        else:
            # Intentar extraer las partes del texto
            from app.nlp_extractor_legal import extract_partes
            partes = extract_partes(str(extracted_answer))
            logger.info(f"extract_partes() resultado: {partes}")

            if partes and isinstance(partes, dict):
                parte_a = partes.get("parte_a", "")
                parte_b = partes.get("parte_b", "")
                # Actualizar el valor extraído para mostrarlo al usuario
                extracted_answer = partes
                logger.info(f"Partes extraídas - parte_a: {parte_a}, parte_b: {parte_b}")
            else:
                # Si no se pudo extraer, intentar división simple por "vs" o "contra"
                text = str(extracted_answer)
                if " vs " in text.lower():
                    parts = text.split(" vs ", 1)
                    parte_a = parts[0].strip()
                    parte_b = parts[1].strip() if len(parts) > 1 else ""
                elif " contra " in text.lower():
                    parts = text.split(" contra ", 1)
                    parte_a = parts[0].strip()
                    parte_b = parts[1].strip() if len(parts) > 1 else ""
                else:
                    parte_a = text
                    parte_b = ""
                logger.warning(f"Extracción manual - parte_a: {parte_a}, parte_b: {parte_b}")

        # Guardar en ambos diccionarios
        session["answers"]["parte_a"] = parte_a
        session["answers"]["parte_b"] = parte_b
        session["extracted_answers"]["parte_a"] = parte_a
        session["extracted_answers"]["parte_b"] = parte_b
        logger.info(f"Partes guardadas en sesión - parte_a: {parte_a}, parte_b: {parte_b}")

    return {
        "next_question": next_q,
        "completed": completed,
        "extracted_value": extracted_answer
    }


@router.post("/generate-path")
async def generate_ursall_path(payload: URSALLGeneratePath) -> Dict:
    """
    Generar ruta y nombre de archivo según estructura URSALL
    """
    file_id = payload.file_id
    answers = payload.answers
    extension = payload.original_extension

    logger.info(f"=== Generando ruta URSALL para file_id: {file_id} ===")
    logger.info(f"Answers recibidas en payload: {answers}")

    # Obtener sesión
    session = ursall_sessions.get(file_id, {})
    logger.info(f"Sesión encontrada: {session is not None}")

    extracted_answers = session.get("extracted_answers", answers)
    logger.info(f"Extracted answers desde sesión: {extracted_answers}")

    # Validar respuestas
    validation = validate_ursall_answers(extracted_answers)
    if not validation["valid"]:
        logger.error(f"Validación fallida. Campos faltantes: {validation['missing']}")
        logger.error(f"Respuestas recibidas: {extracted_answers}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "campos_faltantes",
                "message": f"Faltan campos requeridos: {', '.join(validation['missing'])}",
                "missing_fields": validation['missing'],
                "received_answers": list(extracted_answers.keys()),
                "all_answers": extracted_answers
            }
        )

    tipo_trabajo = validation["tipo_trabajo"]
    client_name = extracted_answers.get("client", "")

    try:
        if tipo_trabajo == "procedimiento":
            # Extraer datos del procedimiento
            fecha = extracted_answers.get("fecha_procedimiento", "")
            year, month = fecha.split("-")[0], fecha.split("-")[1]

            jurisdiccion = extracted_answers.get("jurisdiccion", "")
            juzgado_num = extracted_answers.get("juzgado_num", "")
            demarcacion = extracted_answers.get("demarcacion", "")

            num_proc = extracted_answers.get("num_procedimiento", "")
            num_proc_parts = num_proc.split("/")
            num_procedimiento = num_proc_parts[0]
            year_proc = num_proc_parts[1] if len(num_proc_parts) > 1 else year

            parte_a = extracted_answers.get("parte_a")
            parte_b = extracted_answers.get("parte_b")

            logger.info(f"Parte A extraída: '{parte_a}'")
            logger.info(f"Parte B extraída: '{parte_b}'")

            # Verificar que tenemos los campos requeridos
            if not parte_a or not parte_b:
                logger.error(f"Faltan partes - parte_a: '{parte_a}', parte_b: '{parte_b}'")
                logger.error(f"Campo 'partes' original: {extracted_answers.get('partes')}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "partes_faltantes",
                        "message": "No se pudieron extraer las partes del procedimiento (demandante y demandado)",
                        "parte_a": parte_a or "",
                        "parte_b": parte_b or "",
                        "partes_original": extracted_answers.get("partes", ""),
                        "help": "Asegúrate de proporcionar las partes en formato 'Parte A vs Parte B' o 'Demandante contra Demandado'"
                    }
                )
            materia_proc = extracted_answers.get("materia_proc", "")
            doc_type = extracted_answers.get("doc_type_proc", "")

            # Generar ruta
            path_info = suggest_path_ursall(
                client_name=client_name,
                tipo_trabajo="procedimiento",
                doc_type=doc_type,
                year=year,
                month=month,
                jurisdiccion=jurisdiccion,
                juzgado_num=juzgado_num,
                demarcacion=demarcacion,
                num_procedimiento=num_procedimiento,
                year_proc=year_proc,
                parte_a=parte_a,
                parte_b=parte_b,
                materia_proc=materia_proc
            )

        else:  # proyecto
            # Extraer datos del proyecto
            year = extracted_answers.get("proyecto_year", "")
            month = extracted_answers.get("proyecto_month", "")
            proyecto_nombre = extracted_answers.get("proyecto_nombre", "")
            materia_proyecto = extracted_answers.get("proyecto_materia", "")
            doc_type = extracted_answers.get("doc_type_proyecto", "")

            # Generar ruta
            path_info = suggest_path_ursall(
                client_name=client_name,
                tipo_trabajo="proyecto",
                doc_type=doc_type,
                year=year,
                month=month,
                proyecto_nombre=proyecto_nombre,
                materia_proyecto=materia_proyecto
            )

        # Generar nombre de archivo
        # Formato: {tipo_documento}_{fecha/info}.{ext}
        sanitized_doc_type = sanitize_filename_part(doc_type)

        if tipo_trabajo == "procedimiento":
            fecha = extracted_answers.get("fecha_procedimiento", "")
            suggested_name = f"{fecha}_{sanitized_doc_type}{extension}"
        else:
            year = extracted_answers.get("proyecto_year", "")
            month = extracted_answers.get("proyecto_month", "")
            suggested_name = f"{year}_{month}_{sanitized_doc_type}{extension}"

        full_path = f"{path_info['full_path']}/{suggested_name}"

        return {
            "suggested_name": suggested_name,
            "suggested_path": path_info["full_path"],
            "full_path": full_path,
            "folder_structure": path_info["folder_structure"],
            "tipo": path_info["tipo"],
            "subfolder": path_info["subfolder"]
        }

    except ValueError as e:
        logger.error(f"ValueError generando ruta: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail={
            "error": "valor_invalido",
            "message": str(e),
            "tipo_trabajo": tipo_trabajo
        })
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error generando ruta URSALL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={
            "error": "error_interno",
            "message": f"Error generando ruta: {str(e)}",
            "file_id": file_id,
            "tipo_trabajo": tipo_trabajo if 'tipo_trabajo' in locals() else "desconocido"
        })


@router.post("/upload-final")
async def upload_ursall_final(payload: URSALLUploadFinal) -> Dict:
    """
    Subir archivo a Dropbox según estructura URSALL
    Crea toda la estructura de carpetas necesaria
    """
    from pathlib import Path
    import tempfile
    import os

    file_id = payload.file_id
    filename = payload.filename
    dropbox_path = payload.dropbox_path
    folder_structure = payload.folder_structure

    # Verificar autenticación
    access_token = auth.get_access_token()

    # Obtener archivo temporal
    TEMP_STORAGE_PATH = Path(tempfile.gettempdir()) / "dropbox_chatbot"
    temp_file = None
    for file in TEMP_STORAGE_PATH.glob(f"{file_id}_*"):
        temp_file = file
        break

    if not temp_file or not temp_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Archivo temporal no encontrado: {file_id}"
        )

    try:
        # Crear estructura de carpetas
        from app.dropbox_uploader import create_folder_if_not_exists

        logger.info(f"=== Creando estructura de carpetas URSALL ===")
        logger.info(f"Total de carpetas a crear: {len(folder_structure)}")

        for folder_path in folder_structure:
            await create_folder_if_not_exists(access_token, folder_path)
            logger.info(f"Carpeta creada/verificada: {folder_path}")

        # Subir archivo directamente a dropbox_path (que ya incluye la subcarpeta correcta)
        logger.info(f"=== Subiendo archivo ===")
        logger.info(f"Dropbox path (destino): {dropbox_path}")
        logger.info(f"Filename: {filename}")

        result = await upload_file_to_dropbox(
            access_token=access_token,
            file_path=str(temp_file),
            dropbox_path=dropbox_path,  # Ya es la ruta completa de la subcarpeta
            new_filename=filename
        )

        # Limpiar archivo temporal
        temp_file.unlink()

        # Limpiar sesión
        if file_id in ursall_sessions:
            del ursall_sessions[file_id]

        # Preparar mensaje de respuesta
        message = "Archivo subido exitosamente a Dropbox (estructura URSALL)"
        if result.get("was_renamed"):
            message += f". El archivo fue renombrado a '{result['name']}' porque ya existía uno con el mismo nombre."

        return {
            "success": True,
            "message": message,
            "dropbox_path": result["path"],
            "dropbox_name": result["name"],
            "size": result["size"],
            "folders_created": len(folder_structure),
            "was_renamed": result.get("was_renamed", False),
            "original_filename": filename if result.get("was_renamed") else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo archivo URSALL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error subiendo a Dropbox: {str(e)}"
        )
