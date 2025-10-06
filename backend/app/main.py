"""
FastAPI main application
Refactored for better separation of concerns (AD-1)
AD-2: Question flow endpoints
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import uuid
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.validators import (
    validate_upload_file,
    validate_text_answer,
    validate_date_format,
    sanitize_filename_part,
    FileValidationError,
    # AD-3: Advanced validators
    validate_date_advanced,
    validate_doc_type_advanced,
    validate_client_advanced,
    generate_doc_type_suggestion,
    generate_date_suggestion
)
from app.nlp_extractor import extract_information
from app.gemini_rest_extractor import extract_information_ai, check_gemini_status
from app.questions import (
    get_first_question,
    get_next_question,
    is_last_question
)
from app.path_mapper import suggest_path, get_full_path, suggest_path_intelligent
from app.dropbox_helper import get_existing_structure
from app import auth
from app.dropbox_uploader import upload_file_to_dropbox
from fastapi.responses import RedirectResponse

app = FastAPI(title="Dropbox Chatbot Organizer")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
# Use Windows-compatible temp path
import tempfile
import os
TEMP_STORAGE_PATH = Path(tempfile.gettempdir()) / "dropbox_chatbot"
# Create directory if it doesn't exist
os.makedirs(TEMP_STORAGE_PATH, exist_ok=True)

# In-memory storage for question state (AD-2)
# In production, this would be a database
question_sessions: Dict[str, Dict] = {}


# Pydantic models for AD-2
class QuestionStart(BaseModel):
    file_id: str


class QuestionAnswer(BaseModel):
    file_id: str
    question_id: str
    answer: str


class GenerateName(BaseModel):
    file_id: str
    answers: Dict[str, str]
    original_extension: str


class SuggestPath(BaseModel):
    doc_type: str
    client: str
    date: str


class UploadFinal(BaseModel):
    file_id: str
    new_filename: str
    dropbox_path: str


@app.post("/api/upload-temp")
async def upload_temp(file: UploadFile = File(...)) -> Dict:
    """
    Upload a file to temporary storage

    AD-1: Subir archivo desde el chat
    - Validates file size and extension
    - Saves to /tmp with UUID prefix
    - Returns file metadata
    """
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    # Validate file (refactored to validators module)
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


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "app": "Dropbox Chatbot Organizer API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/upload-temp",
            "questions_start": "POST /api/questions/start",
            "questions_answer": "POST /api/questions/answer",
            "generate_name": "POST /api/questions/generate-name",
            "health": "GET /health",
            "docs": "GET /docs"
        },
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    gemini_status = check_gemini_status()
    return {
        "status": "ok",
        "ai": gemini_status
    }


# AD-5: OAuth2 authentication endpoints
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
        return RedirectResponse(url="http://localhost:5173", status_code=307)
    except HTTPException as e:
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"http://localhost:5173?auth_error={e.detail}",
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


# AD-2: Question flow endpoints
@app.post("/api/questions/start")
async def start_questions(payload: QuestionStart) -> Dict:
    """
    Start question flow for a file
    Returns the first question (doc_type)

    AD-2: Guía por preguntas
    Refactored to use questions module
    """
    file_id = payload.file_id

    # Initialize session
    question_sessions[file_id] = {
        "current_question": "doc_type",
        "answers": {},
        "extracted_answers": {}
    }

    return get_first_question()


@app.post("/api/questions/answer")
async def answer_question(payload: QuestionAnswer) -> Dict:
    """
    Submit answer to a question and get next question

    AD-2: Validates answer and returns next question or completion
    AD-3: Uses advanced validation with suggestions
    Refactored to use questions module
    Updated: Uses NLP extraction to intelligently extract key information
    """
    file_id = payload.file_id
    question_id = payload.question_id
    answer = payload.answer

    # STEP 1: Extract key information from user response using AI
    logger.info(f"Original answer: {answer}")
    try:
        extracted_answer = await extract_information_ai(question_id, answer)
        logger.info(f"Extracted answer: {extracted_answer}")

        # Check for ambiguity
        if extracted_answer == "AMBIGUO":
            # Generate helpful clarification message based on question type
            clarification_messages = {
                "client": "No pude identificar claramente el nombre del cliente. Por favor, proporciona el nombre completo (ej: 'Juan Pérez' o 'Acme Corp S.L.')",
                "doc_type": "No pude identificar el tipo de documento. Por favor, especifica el tipo (ej: 'factura', 'contrato', 'recibo', 'nómina')",
                "date": "No pude identificar una fecha válida. Por favor, usa un formato claro (ej: '15/01/2025' o '2025-01-15')"
            }
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "AMBIGUOUS_RESPONSE",
                    "message": clarification_messages.get(question_id, "Respuesta ambigua, por favor proporciona más información"),
                    "suggestion": "Sé más específico en tu respuesta"
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI extraction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la respuesta: {str(e)}"
        )

    # STEP 2: Validate with advanced validators and generate suggestions on error
    try:
        if question_id == "doc_type":
            validated_answer = validate_doc_type_advanced(extracted_answer)
        elif question_id == "client":
            validated_answer = validate_client_advanced(extracted_answer)
        elif question_id == "date":
            validated_answer, warning = validate_date_advanced(extracted_answer)
            # Note: warning stored but not returned in this endpoint
            # Could be added to response if needed
        else:
            raise HTTPException(status_code=400, detail="Invalid question_id")
    except FileValidationError as e:
        # AD-3: Generate suggestion for common mistakes
        suggestion = None
        if question_id == "doc_type":
            suggestion = generate_doc_type_suggestion(extracted_answer)
        elif question_id == "date":
            suggestion = generate_date_suggestion(extracted_answer)

        # Return error with optional suggestion
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "detail": e.message,
                "suggestion": suggestion
            } if suggestion else e.message
        )

    # Store answer (both extracted and validated)
    if file_id not in question_sessions:
        question_sessions[file_id] = {"answers": {}, "extracted_answers": {}}

    # Ensure extracted_answers key exists (for existing sessions)
    if "extracted_answers" not in question_sessions[file_id]:
        question_sessions[file_id]["extracted_answers"] = {}

    question_sessions[file_id]["answers"][question_id] = validated_answer
    question_sessions[file_id]["extracted_answers"][question_id] = extracted_answer

    # Get next question using refactored logic
    next_q = get_next_question(question_id)
    completed = is_last_question(question_id)

    return {
        "next_question": next_q,
        "completed": completed,
        "extracted_value": extracted_answer,  # Lo que Gemini extrajo
        "validated_value": validated_answer   # Lo que pasó la validación
    }


@app.post("/api/suggest-path")
async def suggest_dropbox_path(payload: SuggestPath) -> Dict:
    """
    Suggest Dropbox path based on document type with intelligent organization

    AD-4: Enhanced path suggestion with year/client subfolders
    """
    doc_type = payload.doc_type
    client = payload.client
    date = payload.date

    # Suggest path with intelligent sub-organization
    suggested_path = suggest_path(doc_type, client=client, date=date)

    # Generate suggested name (for convenience)
    sanitized_type = sanitize_filename_part(doc_type)
    sanitized_client = sanitize_filename_part(client)
    suggested_name = f"{date}_{sanitized_type}_{sanitized_client}.pdf"  # Assume pdf

    # Get full path
    full_path = get_full_path(suggested_path, suggested_name)

    return {
        "suggested_path": suggested_path,
        "suggested_name": suggested_name,
        "full_path": full_path,
        "organization": {
            "by_year": date.split('-')[0] if date else None,
            "by_client": sanitize_filename_part(client) if client else None
        }
    }


@app.post("/api/questions/generate-name")
async def generate_filename(payload: GenerateName) -> Dict:
    """
    Generate suggested filename and intelligent path based on Dropbox structure

    AD-2: Format {fecha}_{tipo}_{cliente}.{ext}
    AD-4: Enhanced path with year/client subfolders
    NEW: Uses extracted Gemini data and existing Dropbox structure
    """
    file_id = payload.file_id
    answers = payload.answers
    extension = payload.original_extension

    # Get extracted answers from Gemini (stored in session)
    session = question_sessions.get(file_id, {})
    extracted_answers = session.get("extracted_answers", answers)

    # Use Gemini-extracted data
    date = extracted_answers.get("date", answers.get("date", ""))
    doc_type = extracted_answers.get("doc_type", answers.get("doc_type", ""))
    client = extracted_answers.get("client", answers.get("client", ""))

    # Sanitize parts
    sanitized_type = sanitize_filename_part(doc_type)
    sanitized_client = sanitize_filename_part(client)

    # Build filename: {date}_{type}_{client}.{ext}
    suggested_name = f"{date}_{sanitized_type}_{sanitized_client}{extension}"

    # Get Dropbox structure and suggest intelligent path
    try:
        access_token = auth.get_access_token()
        dropbox_structure = await get_existing_structure(access_token)
        logger.info(f"Retrieved Dropbox structure: {len(dropbox_structure)} folders")
    except Exception as e:
        logger.warning(f"Could not retrieve Dropbox structure: {e}")
        dropbox_structure = None

    # Use intelligent path suggestion
    path_info = suggest_path_intelligent(
        doc_type=doc_type,
        client=client,
        date=date,
        dropbox_structure=dropbox_structure
    )

    suggested_path = path_info["path"]
    full_path = get_full_path(suggested_path, suggested_name)

    return {
        "suggested_name": suggested_name,
        "original_extension": extension,
        "suggested_path": suggested_path,
        "full_path": full_path,
        "organization": path_info["organization"],
        "matched_existing": path_info["matched_existing"],
        "created_folders": path_info["created_folders"],
        "extracted_data": {
            "doc_type": doc_type,
            "client": client,
            "date": date
        }
    }


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
    import httpx
    import logging

    logger = logging.getLogger(__name__)

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


@app.post("/api/upload-final")
async def upload_final(payload: UploadFinal) -> Dict:
    """
    Upload file to Dropbox with final name and path

    AD-6: US-08 - Subida a Dropbox
    Requires authentication
    """
    # Check authentication
    access_token = auth.get_access_token()

    file_id = payload.file_id
    new_filename = payload.new_filename
    dropbox_path = payload.dropbox_path

    # Get temporary file path
    # File ID format: {uuid}_{original_filename}
    temp_file = None
    for file in TEMP_STORAGE_PATH.glob(f"{file_id}_*"):
        temp_file = file
        break

    if not temp_file or not temp_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Temporary file not found for file_id: {file_id}"
        )

    # Upload to Dropbox
    try:
        result = await upload_file_to_dropbox(
            access_token=access_token,
            file_path=str(temp_file),
            dropbox_path=dropbox_path,
            new_filename=new_filename
        )

        # Clean up temporary file after successful upload
        temp_file.unlink()

        # Clean up question session
        if file_id in question_sessions:
            del question_sessions[file_id]

        return {
            "success": True,
            "message": "Archivo subido exitosamente a Dropbox",
            "dropbox_path": result["path"],
            "dropbox_name": result["name"],
            "size": result["size"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading to Dropbox: {str(e)}"
        )

