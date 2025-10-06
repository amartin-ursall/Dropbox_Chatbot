"""
Gemini AI Extractor - Intelligent information extraction using Google Gemini API
Extracts key information from user responses using AI
"""
import os
import logging
from typing import Optional, Dict
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Flag to check if Gemini is available
GEMINI_AVAILABLE = False

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Use gemini-pro (stable, compatible with version 0.3.2)
        model = genai.GenerativeModel('gemini-pro')
        GEMINI_AVAILABLE = True
        logger.info("Gemini API initialized successfully with gemini-pro")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini API: {e}")
        logger.error("System will not work without Gemini")
        GEMINI_AVAILABLE = False
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")
    logger.warning("Falling back to regex-based extraction")


def extract_with_gemini(question_id: str, user_input: str) -> Optional[str]:
    """
    Extract information using Gemini AI

    Args:
        question_id: Type of question (doc_type, client, date)
        user_input: Raw user response

    Returns:
        Extracted information or None if failed
    """
    if not GEMINI_AVAILABLE:
        return None

    # Define prompts for each question type
    prompts = {
        "client": """Extrae ÚNICAMENTE el nombre del cliente de la siguiente respuesta del usuario.
Reglas:
- Si el usuario dice "El cliente es Acme Corp", devuelve solo "Acme Corp"
- Si dice "Juan Pérez", devuelve "Juan Pérez"
- Si dice "se llama Microsoft España S.L.", devuelve "Microsoft España S.L."
- Elimina palabras como "cliente", "nombre", "es", "se llama", etc.
- Mantén puntos, guiones, y caracteres especiales en nombres de empresas
- NO añadas explicaciones, solo devuelve el nombre extraído

Respuesta del usuario: "{user_input}"

Nombre del cliente:""",

        "doc_type": """Extrae ÚNICAMENTE el tipo de documento de la siguiente respuesta del usuario.
Reglas:
- Si el usuario dice "Es una factura", devuelve solo "factura"
- Si dice "Contrato", devuelve "contrato"
- Si dice "son presupuestos", devuelve "presupuestos"
- Elimina artículos (un, una, el, la) y palabras como "tipo", "documento", "es"
- Devuelve en singular y minúsculas
- Tipos comunes: factura, contrato, recibo, nómina, presupuesto, albarán
- NO añadas explicaciones, solo devuelve el tipo extraído

Respuesta del usuario: "{user_input}"

Tipo de documento:""",

        "date": """Extrae ÚNICAMENTE la fecha de la siguiente respuesta del usuario y conviértela al formato YYYY-MM-DD.
Reglas:
- Si el usuario dice "2025-01-15", devuelve "2025-01-15"
- Si dice "15/01/2025", convierte a "2025-01-15"
- Si dice "15-01-2025", convierte a "2025-01-15"
- Si dice "La fecha es 31/12/2024", devuelve "2024-12-31"
- Formato final SIEMPRE: YYYY-MM-DD
- NO añadas explicaciones, solo devuelve la fecha en formato YYYY-MM-DD

Respuesta del usuario: "{user_input}"

Fecha (YYYY-MM-DD):"""
    }

    prompt = prompts.get(question_id)
    if not prompt:
        logger.warning(f"No prompt defined for question_id: {question_id}")
        return None

    # Format prompt with user input
    formatted_prompt = prompt.format(user_input=user_input)

    try:
        # Generate response
        response = model.generate_content(
            formatted_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for more deterministic output
                max_output_tokens=50,  # Short response expected
            )
        )

        # Check if response is valid
        if not response or not hasattr(response, 'text'):
            logger.error("Gemini returned empty or invalid response")
            return None

        # Extract text and clean
        try:
            extracted = response.text.strip()
        except Exception as text_error:
            logger.error(f"Error accessing response.text: {text_error}")
            # Try accessing candidates directly
            if hasattr(response, 'candidates') and response.candidates:
                try:
                    extracted = response.candidates[0].content.parts[0].text.strip()
                except Exception:
                    logger.error("Could not extract text from candidates")
                    return None
            else:
                return None

        if not extracted:
            logger.error("Gemini returned empty text")
            return None

        # Remove common unwanted prefixes/suffixes that AI might add
        extracted = extracted.replace("**", "").replace("*", "")
        extracted = extracted.strip('"').strip("'").strip()

        logger.info(f"Gemini extraction - Input: '{user_input}' -> Output: '{extracted}'")

        return extracted

    except Exception as e:
        logger.error(f"Gemini API error: {e}", exc_info=True)
        return None


def extract_information_ai(question_id: str, user_input: str) -> str:
    """
    Main extraction function - Uses ONLY Gemini AI

    Args:
        question_id: Type of question (doc_type, client, date)
        user_input: Raw user response

    Returns:
        Extracted information using Gemini AI

    Raises:
        Exception: If Gemini is not available or extraction fails
    """
    if not GEMINI_AVAILABLE:
        raise Exception(
            "Gemini API is not configured. Please set GEMINI_API_KEY in your .env file. "
            "Get your free API key at: https://aistudio.google.com/app/apikey"
        )

    extracted = extract_with_gemini(question_id, user_input)
    if not extracted:
        raise Exception("Gemini extraction failed. Please try again.")

    logger.info(f"✓ Gemini AI extraction for {question_id}: '{extracted}'")
    return extracted


def check_gemini_status() -> Dict[str, any]:
    """
    Check if Gemini API is available and working

    Returns:
        Dict with status information
    """
    return {
        "gemini_available": GEMINI_AVAILABLE,
        "api_key_configured": bool(GEMINI_API_KEY),
        "required": True,
        "setup_url": "https://aistudio.google.com/app/apikey" if not GEMINI_AVAILABLE else None
    }
