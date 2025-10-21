"""
Gemini AI Extractor using REST API directly
More compatible than SDK
"""
import os
import logging
import httpx
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_AVAILABLE = bool(GEMINI_API_KEY)

if GEMINI_AVAILABLE:
    logger.info("Gemini API key configured, using REST API")
else:
    logger.warning("GEMINI_API_KEY not found")


async def extract_with_gemini_rest(question_id: str, user_input: str) -> Optional[str]:
    """
    Extract information using Gemini REST API

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
        "tipo_trabajo": f"""Eres un asistente experto en clasificar tipos de trabajo legal en español.

TAREA: Determina si el usuario se refiere a un PROCEDIMIENTO JUDICIAL o un PROYECTO JURÍDICO.

REGLAS ESTRICTAS:
1. Si menciona: demanda, juicio, procedimiento judicial, recurso, juzgado, tribunal → responde "procedimiento"
2. Si menciona: proyecto, asesoría, consultoría, informe, opinión legal, dictamen → responde "proyecto"
3. Si es ambiguo o no está claro, responde exactamente: "AMBIGUO"
4. Responde SOLO con: "procedimiento", "proyecto" o "AMBIGUO"

EJEMPLOS:
- "Es un procedimiento judicial" → procedimiento
- "Un juicio" → procedimiento
- "Proyecto de asesoría" → proyecto
- "Es para un informe legal" → proyecto
- "no sé" → AMBIGUO

ENTRADA DEL USUARIO: "{user_input}"

RESPUESTA (procedimiento, proyecto o AMBIGUO):""",

        "client": f"""Eres un asistente experto en extraer nombres de clientes de texto en español.

TAREA: Extrae ÚNICAMENTE el nombre del cliente de la siguiente entrada del usuario.

REGLAS ESTRICTAS:
1. Extrae solo el nombre del cliente, empresa u organización
2. Elimina completamente palabras como: "el cliente", "se llama", "nombre", "es", "se denomina"
3. Mantén nombres completos con apellidos, puntos, guiones y símbolos corporativos (S.L., S.A., Inc., Corp., &, etc.)
4. Si hay múltiples nombres mencionados, extrae solo el que sea el cliente
5. Si la entrada es ambigua o no contiene un nombre claro, responde exactamente: "AMBIGUO"
6. NO añadas puntos, comas ni explicaciones adicionales

EJEMPLOS:
- "El cliente es Juan Pérez" → Juan Pérez
- "se llama Microsoft España S.L." → Microsoft España S.L.
- "nombre del cliente: Acme Corp" → Acme Corp
- "Tech & Solutions Inc." → Tech & Solutions Inc.
- "no sé" → AMBIGUO
- "después te digo" → AMBIGUO

ENTRADA DEL USUARIO: "{user_input}"

RESPUESTA (solo el nombre del cliente o AMBIGUO):""",

        "doc_type": f"""Eres un asistente experto en clasificar tipos de documentos en español.

TAREA: Extrae ÚNICAMENTE el tipo de documento de la siguiente entrada del usuario.

REGLAS ESTRICTAS:
1. Extrae solo el tipo de documento
2. Elimina artículos (un, una, el, la, los, las) y palabras introductorias
3. Convierte a singular y minúsculas
4. Normaliza variaciones: "facturas" → "factura", "contratos" → "contrato"
5. Tipos comunes: factura, contrato, recibo, nómina, presupuesto, albarán, pedido, nota, certificado, escritura
6. Si menciona categorías amplias (jurídico, legal, financiero), úsalas como tipo
7. Si la entrada es ambigua o no contiene un tipo claro, responde exactamente: "AMBIGUO"
8. NO añadas explicaciones adicionales

EJEMPLOS:
- "Es una factura" → factura
- "son contratos" → contrato
- "documento jurídico" → juridico
- "tipo de documento: presupuesto" → presupuesto
- "no estoy seguro" → AMBIGUO
- "varios tipos" → AMBIGUO

ENTRADA DEL USUARIO: "{user_input}"

RESPUESTA (solo el tipo en singular y minúsculas, o AMBIGUO):""",

        "date": f"""Eres un asistente experto en extraer y normalizar fechas en español.

TAREA: Extrae la fecha de la siguiente entrada del usuario y conviértela al formato YYYY-MM-DD.

REGLAS ESTRICTAS:
1. Extrae cualquier fecha mencionada
2. Convierte SIEMPRE al formato: YYYY-MM-DD (año-mes-día)
3. Formatos aceptados de entrada:
   - DD/MM/YYYY (15/01/2025 → 2025-01-15)
   - DD-MM-YYYY (15-01-2025 → 2025-01-15)
   - YYYY-MM-DD (ya está correcto)
   - Fechas en palabras: "15 de enero de 2025" → 2025-01-15
4. Si la entrada es ambigua, incompleta o no contiene una fecha clara, responde exactamente: "AMBIGUO"
5. NO añadas explicaciones adicionales
6. Asume año 2025 si solo se menciona día y mes

EJEMPLOS:
- "La fecha es 15/01/2025" → 2025-01-15
- "31-12-2024" → 2024-12-31
- "2025-01-15" → 2025-01-15
- "15 de enero" → 2025-01-15
- "ayer" → AMBIGUO
- "no recuerdo" → AMBIGUO
- "15/13/2025" (mes inválido) → AMBIGUO

ENTRADA DEL USUARIO: "{user_input}"

RESPUESTA (formato YYYY-MM-DD o AMBIGUO):""",

        "doc_type_proc": f"""Eres un asistente experto en clasificar documentos judiciales en español.

TAREA: Extrae el tipo de documento judicial de la entrada del usuario.

TIPOS COMUNES:
- Demanda, Contestación, Escrito de conclusiones, Recurso de apelación, Recurso de casación
- Sentencia, Auto, Providencia, Diligencia
- Prueba documental, Prueba pericial, Prueba testifical

REGLAS:
1. Extrae solo el tipo de documento
2. Elimina artículos y palabras introductorias
3. Mantén formato apropiado con mayúsculas (ej: "Demanda", "Recurso de apelación")
4. Si es ambiguo, responde "AMBIGUO"

EJEMPLOS:
- "Es una demanda" → Demanda
- "escrito de contestación" → Contestación
- "Un recurso de apelación" → Recurso de apelación
- "no sé" → AMBIGUO

ENTRADA DEL USUARIO: "{user_input}"

RESPUESTA:""",

        "doc_type_proyecto": f"""Eres un asistente experto en clasificar documentos de proyectos jurídicos.

TAREA: Extrae el tipo de documento de proyecto legal.

TIPOS COMUNES:
- Informe jurídico, Dictamen, Opinión legal, Memoria
- Contrato, Convenio, Acuerdo
- Estatutos, Reglamento, Política
- Documento de trabajo, Borrador

REGLAS:
1. Extrae solo el tipo de documento
2. Elimina artículos y palabras introductorias
3. Mantén formato apropiado con mayúsculas
4. Si es ambiguo, responde "AMBIGUO"

EJEMPLOS:
- "Es un informe jurídico" → Informe jurídico
- "Un contrato" → Contrato
- "Borrador de convenio" → Convenio
- "no estoy seguro" → AMBIGUO

ENTRADA DEL USUARIO: "{user_input}"

RESPUESTA:"""
    }

    prompt = prompts.get(question_id)
    if not prompt:
        return None

    # Gemini REST API endpoint (using gemini-2.5-flash-lite - free tier)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 50,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)

            if response.status_code != 200:
                logger.error(f"Gemini API error {response.status_code}: {response.text}")
                return None

            data = response.json()

            # Extract text from response
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        extracted = parts[0]["text"].strip()

                        # Clean up
                        extracted = extracted.replace("**", "").replace("*", "")
                        extracted = extracted.strip('"').strip("'").strip()

                        # Check for ambiguity
                        if extracted.upper() == "AMBIGUO":
                            logger.warning(f"Ambiguous response detected for '{user_input}'")
                            return "AMBIGUO"

                        logger.info(f"Gemini REST extraction - Input: '{user_input}' -> Output: '{extracted}'")
                        return extracted

            logger.error(f"Unexpected response format: {data}")
            return None

    except Exception as e:
        logger.error(f"Gemini REST API error: {e}", exc_info=True)
        return None


async def extract_information_ai(question_id: str, user_input: str) -> str:
    """
    Main extraction function - Uses Gemini REST API

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

    extracted = await extract_with_gemini_rest(question_id, user_input)
    if not extracted:
        raise Exception("Gemini extraction failed. Please try again.")

    logger.info(f"✓ Gemini AI extraction for {question_id}: '{extracted}'")
    return extracted


def check_gemini_status() -> dict:
    """
    Check if Gemini API is available

    Returns:
        Dict with status information
    """
    return {
        "gemini_available": GEMINI_AVAILABLE,
        "api_key_configured": bool(GEMINI_API_KEY),
        "required": True,
        "api_type": "REST",
        "setup_url": "https://aistudio.google.com/app/apikey" if not GEMINI_AVAILABLE else None
    }
