"""
FastAPI main application - URSALL Legal System
Sistema unificado con funcionalidad completa URSALL
Maneja procedimientos judiciales y proyectos jurídicos
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Optional
import uuid
import logging
import tempfile
import os
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports
from app.validators import validate_upload_file, sanitize_filename_part, FileValidationError
from app.questions_ursall import (
    get_first_question_ursall,
    get_next_question_ursall,
    is_last_question_ursall,
    validate_ursall_answers
)
from app.nlp_extractor_legal import extract_information_legal, extract_partes
from app.path_mapper_ursall import suggest_path_ursall
from app import auth
from app.dropbox_uploader import upload_file_to_dropbox, create_folder_if_not_exists
from app.gemini_rest_extractor import check_gemini_status

# Create FastAPI app
app = FastAPI(title="Dropbox AI Organizer - URSALL Legal System")

# CORS middleware for frontend
# Support both development and production URLs with network access
FRONTEND_URLS = os.getenv("FRONTEND_URLS", "").split(",") if os.getenv("FRONTEND_URLS") else [
    "http://localhost:5173",
    "https://localhost:5173",
    "https://localhost",
    "http://dropboxaiorganizer.com:5173",
    "https://dropboxaiorganizer.com:5173",
    "https://dropboxaiorganizer.com",
    "http://dropboxaiorganizer.com",
    # Allow access from any IP on the network with domain
    "http://*:5173",
    "https://*:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Configuration
TEMP_STORAGE_PATH = Path(tempfile.gettempdir()) / "dropbox_chatbot"
os.makedirs(TEMP_STORAGE_PATH, exist_ok=True)

# In-memory storage for question sessions (in production, use database)
ursall_sessions: Dict[str, Dict] = {}


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class QuestionStart(BaseModel):
    file_id: str


class QuestionAnswer(BaseModel):
    file_id: str
    question_id: str
    answer: str


class GeneratePath(BaseModel):
    file_id: str
    answers: Dict[str, str]
    original_extension: str


class UploadFinal(BaseModel):
    file_id: str
    filename: str
    dropbox_path: str
    folder_structure: list


# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "app": "Dropbox AI Organizer - URSALL Legal System",
        "version": "2.0.0",
        "system": "URSALL",
        "endpoints": {
            "upload": "POST /api/upload-temp",
            "questions_start": "POST /api/questions/start",
            "questions_answer": "POST /api/questions/answer",
            "generate_path": "POST /api/questions/generate-path",
            "upload_final": "POST /api/upload-final",
            "user_info": "GET /api/user/info",
            "health": "GET /health",
            "docs": "GET /docs",
            "auth_login": "GET /auth/dropbox/login",
            "auth_status": "GET /auth/status"
        },
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    gemini_status = check_gemini_status()
    return {
        "status": "ok",
        "system": "URSALL",
        "ai": gemini_status
    }


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.get("/auth/dropbox/login")
async def dropbox_login():
    """
    Initiate Dropbox OAuth2 flow
    Redirects user to Dropbox authorization page
    """
    auth_url = auth.generate_auth_url()
    return RedirectResponse(url=auth_url, status_code=307)


@app.get("/auth/dropbox/callback")
async def dropbox_callback(code: str):
    """
    OAuth2 callback endpoint
    Exchanges authorization code for access token
    """
    try:
        # Exchange code for token
        token_data = await auth.exchange_code_for_token(code)

        # Store in session
        auth.store_session(token_data)

        # Redirect to frontend
        frontend_url = os.getenv("FRONTEND_URL", "http://dropboxaiorganizer.com:5173")
        return RedirectResponse(url=frontend_url, status_code=307)
    except HTTPException as e:
        # Redirect to frontend with error
        frontend_url = os.getenv("FRONTEND_URL", "http://dropboxaiorganizer.com:5173")
        return RedirectResponse(
            url=f"{frontend_url}?auth_error={e.detail}",
            status_code=307
        )


@app.get("/auth/status")
async def auth_status():
    """
    Check authentication status
    Returns whether user is authenticated and account info
    """
    session = auth.get_session()
    if session:
        return {
            "authenticated": True,
            "account_id": session.get("account_id")
        }
    return {
        "authenticated": False,
        "account_id": None
    }


@app.post("/auth/logout")
async def logout():
    """
    Logout user
    Clears session data
    """
    auth.clear_session()
    return {"success": True}


# ============================================================================
# FILE UPLOAD ENDPOINT
# ============================================================================

@app.post("/api/upload-temp")
async def upload_temp(file: UploadFile = File(...)) -> Dict:
    """
    Upload a file to temporary storage

    - Validates file size and extension
    - Saves to temp with UUID prefix
    - Returns file metadata
    """
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    # Validate file
    try:
        file_extension, _ = validate_upload_file(file.filename, file_size)
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # Generate unique file ID
    file_id = str(uuid.uuid4())

    # Save to temporary storage
    temp_file_path = TEMP_STORAGE_PATH / f"{file_id}_{file.filename}"
    temp_file_path.write_bytes(file_content)

    # Return metadata
    return {
        "file_id": file_id,
        "original_name": file.filename,
        "size": file_size,
        "extension": file_extension
    }


# ============================================================================
# URSALL QUESTION FLOW ENDPOINTS
# ============================================================================

@app.post("/api/questions/start")
async def start_questions(payload: QuestionStart) -> Dict:
    """
    Start URSALL question flow
    Returns the first question (tipo_trabajo)
    """
    file_id = payload.file_id

    # Initialize session
    ursall_sessions[file_id] = {
        "current_question": "tipo_trabajo",
        "answers": {},
        "extracted_answers": {}
    }

    return get_first_question_ursall()


@app.post("/api/questions/answer")
async def answer_question(payload: QuestionAnswer) -> Dict:
    """
    Answer a question in the URSALL flow
    Extracts information using legal NLP and validates
    """
    file_id = payload.file_id
    question_id = payload.question_id
    answer = payload.answer

    # Verify session
    if file_id not in ursall_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    session = ursall_sessions[file_id]

    # STEP 1: Extract information using legal NLP
    logger.info(f"Respuesta original: {answer}")

    try:
        extracted_answer = extract_information_legal(question_id, answer)
        logger.info(f"Información extraída: {extracted_answer}")
    except Exception as e:
        logger.error(f"Error en extracción NLP: {e}")
        extracted_answer = answer.strip()

    # STEP 2: Basic validations with clear error messages
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

    # STEP 3: Specific validations per question type with clear messages
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
        # Validate format XXX/YYYY
        import re
        if not re.match(r'^\d+/\d{4}$', str(extracted_answer)):
            raise HTTPException(
                status_code=400,
                detail="Formato inválido. Debe ser XXX/YYYY (ej: 455/2025)"
            )

    elif question_id in ["proyecto_year", "fecha_procedimiento"]:
        # Validate year or date
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

    # STEP 4: Store answer
    session["answers"][question_id] = extracted_answer
    session["extracted_answers"][question_id] = extracted_answer

    # STEP 5: Get next question
    next_q = get_next_question_ursall(question_id, session["answers"])
    completed = is_last_question_ursall(question_id)

    # STEP 6: If "partes", extract parte_a and parte_b
    if question_id == "partes":
        logger.info(f"Procesando campo 'partes': {extracted_answer}")

        # If extractor already returned a dict with parts
        if isinstance(extracted_answer, dict):
            parte_a = extracted_answer.get("parte_a", "")
            parte_b = extracted_answer.get("parte_b", "")
            logger.info(f"Extractor devolvió partes - parte_a: {parte_a}, parte_b: {parte_b}")
        else:
            # Try to extract parts from text
            partes = extract_partes(str(extracted_answer))
            logger.info(f"extract_partes() resultado: {partes}")

            if partes and isinstance(partes, dict):
                parte_a = partes.get("parte_a", "")
                parte_b = partes.get("parte_b", "")
                # Update extracted value to show to user
                extracted_answer = partes
                logger.info(f"Partes extraídas - parte_a: {parte_a}, parte_b: {parte_b}")
            else:
                # If couldn't extract, try simple split by "vs" or "contra"
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

        # Save in both dictionaries
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


@app.post("/api/questions/generate-path")
async def generate_path(payload: GeneratePath) -> Dict:
    """
    Generate path and filename according to URSALL structure
    """
    file_id = payload.file_id
    answers = payload.answers
    extension = payload.original_extension

    logger.info(f"=== Generando ruta URSALL para file_id: {file_id} ===")
    logger.info(f"Answers recibidas en payload: {answers}")

    # Get session
    session = ursall_sessions.get(file_id, {})
    logger.info(f"Sesión encontrada: {session is not None}")

    extracted_answers = session.get("extracted_answers", answers)
    logger.info(f"Extracted answers desde sesión: {extracted_answers}")

    # Validate answers
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
            # Extract procedure data
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

            # Verify required fields
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

            # Generate path
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
            # Extract project data
            year = extracted_answers.get("proyecto_year", "")
            month = extracted_answers.get("proyecto_month", "")
            proyecto_nombre = extracted_answers.get("proyecto_nombre", "")
            materia_proyecto = extracted_answers.get("proyecto_materia", "")
            doc_type = extracted_answers.get("doc_type_proyecto", "")

            # Generate path
            path_info = suggest_path_ursall(
                client_name=client_name,
                tipo_trabajo="proyecto",
                doc_type=doc_type,
                year=year,
                month=month,
                proyecto_nombre=proyecto_nombre,
                materia_proyecto=materia_proyecto
            )

        # Generate filename
        # Format: {document_type}_{date/info}.{ext}
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


# ============================================================================
# USER INFO ENDPOINT
# ============================================================================

@app.get("/api/user/info")
async def get_user_info() -> Dict:
    """
    Get Dropbox user account information

    Returns:
    - name: User's display name
    - email: User's email
    - used_space: Used storage in bytes
    - allocated_space: Total allocated storage in bytes
    - account_type: Account type (basic, pro, business)
    """
    # Check authentication
    try:
        access_token = auth.get_access_token()
    except HTTPException as e:
        logger.error(f"Authentication error: {e.detail}")
        raise

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            # Get account info
            logger.info("Fetching Dropbox account info...")
            account_response = await client.post(
                "https://api.dropboxapi.com/2/users/get_current_account",
                headers=headers,
                content=b"null"
            )

            if account_response.status_code != 200:
                error_detail = account_response.text
                logger.error(f"Dropbox API error (account): {account_response.status_code} - {error_detail}")
                try:
                    error_json = account_response.json()
                    error_msg = error_json.get("error_summary", error_detail)
                except:
                    error_msg = error_detail
                raise HTTPException(
                    status_code=account_response.status_code,
                    detail=f"Error fetching Dropbox account info: {error_msg}"
                )

            account_data = account_response.json()
            logger.info(f"Account data retrieved for: {account_data.get('email', 'unknown')}")

            # Get space usage
            logger.info("Fetching Dropbox space usage...")
            space_response = await client.post(
                "https://api.dropboxapi.com/2/users/get_space_usage",
                headers=headers,
                content=b"null"
            )

            if space_response.status_code != 200:
                error_detail = space_response.text
                logger.error(f"Dropbox API error (space): {space_response.status_code} - {error_detail}")
                # Continue without space info if it fails
                space_data = {"used": 0, "allocation": {"allocated": 0}}
            else:
                space_data = space_response.json()

            # Extract relevant information
            name = account_data.get("name", {}).get("display_name", "Usuario")
            email = account_data.get("email", "")
            account_type = account_data.get("account_type", {}).get(".tag", "basic")
            profile_photo_url = account_data.get("profile_photo_url", None)

            # Space usage
            used_space = space_data.get("used", 0)
            allocated_space = space_data.get("allocation", {}).get("allocated", 0)

            logger.info(f"User info successfully retrieved for {email}")

            result = {
                "name": name,
                "email": email,
                "used_space": used_space,
                "allocated_space": allocated_space,
                "account_type": account_type.capitalize()
            }

            # Add profile photo URL if available
            if profile_photo_url:
                result["profile_photo_url"] = profile_photo_url

            return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_user_info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user info: {str(e)}"
        )


# ============================================================================
# UPLOAD FINAL ENDPOINT
# ============================================================================

@app.post("/api/upload-final")
async def upload_final(payload: UploadFinal) -> Dict:
    """
    Upload file to Dropbox according to URSALL structure
    Creates all necessary folder structure
    """
    file_id = payload.file_id
    filename = payload.filename
    dropbox_path = payload.dropbox_path
    folder_structure = payload.folder_structure

    # Verify authentication
    access_token = auth.get_access_token()

    # Get temporary file
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
        # Create folder structure
        logger.info(f"=== Creando estructura de carpetas URSALL ===")
        logger.info(f"Total de carpetas a crear: {len(folder_structure)}")

        for folder_path in folder_structure:
            await create_folder_if_not_exists(access_token, folder_path)
            logger.info(f"Carpeta creada/verificada: {folder_path}")

        # Upload file directly to dropbox_path (already includes correct subfolder)
        logger.info(f"=== Subiendo archivo ===")
        logger.info(f"Dropbox path (destino): {dropbox_path}")
        logger.info(f"Filename: {filename}")

        result = await upload_file_to_dropbox(
            access_token=access_token,
            file_path=str(temp_file),
            dropbox_path=dropbox_path,  # Already full path of subfolder
            new_filename=filename
        )

        # Clean up temporary file
        temp_file.unlink()

        # Clean up session
        if file_id in ursall_sessions:
            del ursall_sessions[file_id]

        # Prepare response message
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
