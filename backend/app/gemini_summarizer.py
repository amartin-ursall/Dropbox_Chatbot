"""
Gemini Document Summarizer
Uses Gemini AI to create intelligent document summaries and previews
"""

import os
import logging
import httpx
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_AVAILABLE = bool(GEMINI_API_KEY)

if GEMINI_AVAILABLE:
    logger.info("Gemini API key configured for document summarization")
else:
    logger.warning("GEMINI_API_KEY not found - document summarization unavailable")


async def summarize_document(
    document_text: str,
    document_metadata: Dict,
    target_use: str = "legal"
) -> Optional[Dict]:
    """
    Create an intelligent document summary using Gemini AI

    Args:
        document_text: Full extracted text from document
        document_metadata: Metadata dict with keys:
            - pages: Number of pages
            - has_tables: Boolean
            - has_figures: Boolean
        target_use: Type of use case ("legal", "general")

    Returns:
        Dict with structure:
        {
            "summary": str,  # 2-3 sentence summary
            "document_type": str,  # Identified document type
            "key_information": Dict,  # Extracted key info
            "confidence": float,  # 0-1 confidence score
            "is_legal_document": bool,
            "suggested_answers": Dict  # Suggested answers for URSALL questions
        }
        Or None if failed
    """
    if not GEMINI_AVAILABLE:
        logger.warning("Gemini not available for summarization")
        return None

    # Build prompt based on target use
    if target_use == "legal":
        prompt = _build_legal_summary_prompt(document_text, document_metadata)
    else:
        prompt = _build_general_summary_prompt(document_text, document_metadata)

    try:
        # Use Gemini REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1000,
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
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
                        result_text = parts[0]["text"].strip()

                        # Parse structured response
                        parsed_result = _parse_gemini_summary_response(result_text)

                        logger.info(f"Document summarized successfully: {parsed_result.get('document_type', 'unknown')}")
                        return parsed_result

            logger.error(f"Unexpected Gemini response format: {data}")
            return None

    except Exception as e:
        logger.error(f"Error in document summarization: {e}", exc_info=True)
        return None


def _build_legal_summary_prompt(document_text: str, metadata: Dict) -> str:
    """Build prompt for legal document summarization"""

    # Truncate text if too long (keep first 3000 chars)
    text_sample = document_text[:3000] if len(document_text) > 3000 else document_text

    prompt = f"""Eres un asistente experto en análisis de documentos legales españoles.

TAREA: Analiza el siguiente documento y proporciona un resumen estructurado.

INFORMACIÓN DEL DOCUMENTO:
- Número de páginas: {metadata.get('pages', 1)}
- Contiene tablas: {'Sí' if metadata.get('has_tables') else 'No'}
- Contiene figuras: {'Sí' if metadata.get('has_figures') else 'No'}

TEXTO DEL DOCUMENTO:
{text_sample}

PROPORCIONA UNA RESPUESTA EN FORMATO JSON con la siguiente estructura EXACTA:
{{
  "summary": "Resumen breve del documento en 2-3 frases",
  "document_type": "tipo específico (escritura, demanda, sentencia, contrato, poder, etc.)",
  "is_legal_document": true o false,
  "confidence": 0.0 a 1.0,
  "key_information": {{
    "partes": ["Parte A", "Parte B"] o null,
    "jurisdiccion": "Social/Civil/Penal/Contencioso-Administrativo/Mercantil" o null,
    "juzgado": "nombre del juzgado" o null,
    "numero_procedimiento": "XXX/YYYY" o null,
    "fecha_documento": "YYYY-MM-DD" o null,
    "materia": "breve descripción de la materia" o null
  }},
  "suggested_answers": {{
    "client": "nombre del cliente si es identificable" o null,
    "partes": "Parte A vs Parte B" o null,
    "jurisdiccion": "jurisdicción identificada" o null,
    "materia": "materia identificada" o null
  }}
}}

REGLAS IMPORTANTES:
1. Responde SOLO con JSON válido, sin markdown ni explicaciones
2. Si no puedes identificar un campo, usa null
3. La confianza debe reflejar qué tan seguro estás del análisis
4. is_legal_document debe ser true solo si es claramente un documento legal/judicial
5. Para partes, intenta identificar demandante/actor y demandado
6. Para jurisdicción, identifica si es Social, Civil, Penal, Contencioso-Administrativo o Mercantil
7. Para número de procedimiento, busca patrones como XXX/YYYY o similar

RESPUESTA JSON:"""

    return prompt


def _build_general_summary_prompt(document_text: str, metadata: Dict) -> str:
    """Build prompt for general document summarization"""

    # Truncate text if too long
    text_sample = document_text[:3000] if len(document_text) > 3000 else document_text

    prompt = f"""Eres un asistente experto en análisis de documentos.

TAREA: Analiza el siguiente documento y proporciona un resumen estructurado.

INFORMACIÓN DEL DOCUMENTO:
- Número de páginas: {metadata.get('pages', 1)}
- Contiene tablas: {'Sí' if metadata.get('has_tables') else 'No'}
- Contiene figuras: {'Sí' if metadata.get('has_figures') else 'No'}

TEXTO DEL DOCUMENTO:
{text_sample}

PROPORCIONA UNA RESPUESTA EN FORMATO JSON con la siguiente estructura EXACTA:
{{
  "summary": "Resumen breve del documento en 2-3 frases",
  "document_type": "tipo específico (factura, contrato, presupuesto, informe, etc.)",
  "is_legal_document": false,
  "confidence": 0.0 a 1.0,
  "key_information": {{
    "cliente": "nombre del cliente" o null,
    "fecha": "YYYY-MM-DD" o null,
    "importe": "cantidad con moneda" o null,
    "concepto": "concepto principal" o null
  }},
  "suggested_answers": {{
    "client": "nombre del cliente si es identificable" o null,
    "doc_type": "tipo de documento normalizado" o null,
    "date": "fecha en formato YYYY-MM-DD" o null
  }}
}}

REGLAS IMPORTANTES:
1. Responde SOLO con JSON válido, sin markdown ni explicaciones
2. Si no puedes identificar un campo, usa null
3. La confianza debe reflejar qué tan seguro estás del análisis
4. is_legal_document debe ser false para documentos no legales

RESPUESTA JSON:"""

    return prompt


def _parse_gemini_summary_response(response_text: str) -> Dict:
    """
    Parse Gemini's JSON response into structured dict

    Args:
        response_text: Raw text response from Gemini

    Returns:
        Parsed dictionary
    """
    import json
    import re

    # Clean markdown if present
    response_text = response_text.strip()

    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        # Extract content between ``` markers
        match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response_text, re.DOTALL)
        if match:
            response_text = match.group(1)
        else:
            # Fallback: remove first and last lines
            lines = response_text.split('\n')
            if len(lines) > 2:
                response_text = '\n'.join(lines[1:-1])

    try:
        parsed = json.loads(response_text)

        # Validate structure and provide defaults
        result = {
            "summary": parsed.get("summary", "Resumen no disponible"),
            "document_type": parsed.get("document_type", "documento"),
            "is_legal_document": parsed.get("is_legal_document", False),
            "confidence": float(parsed.get("confidence", 0.5)),
            "key_information": parsed.get("key_information", {}),
            "suggested_answers": parsed.get("suggested_answers", {})
        }

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini JSON response: {e}")
        logger.error(f"Response text: {response_text}")

        # Return fallback structure
        return {
            "summary": "No se pudo generar resumen automático",
            "document_type": "documento",
            "is_legal_document": False,
            "confidence": 0.0,
            "key_information": {},
            "suggested_answers": {}
        }


async def quick_document_check(document_text: str) -> Dict:
    """
    Quick check to determine if document is legal and suitable for URSALL

    Args:
        document_text: Extracted document text

    Returns:
        Dict with:
        {
            "is_legal": bool,
            "confidence": float,
            "suggested_workflow": "ursall" or "standard"
        }
    """
    if not GEMINI_AVAILABLE:
        return {
            "is_legal": False,
            "confidence": 0.0,
            "suggested_workflow": "standard"
        }

    # Quick prompt for legal document detection
    text_sample = document_text[:1500]

    prompt = f"""Determina si este es un documento legal/judicial español.

TEXTO:
{text_sample}

Responde SOLO con JSON:
{{
  "is_legal": true o false,
  "confidence": 0.0 a 1.0,
  "reason": "breve explicación"
}}

Un documento es legal si es: demanda, sentencia, escrito judicial, contrato legal, poder notarial, escritura, resolución judicial, etc.
NO son legales: facturas, presupuestos, informes empresariales, correos, etc."""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 200,
            }
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    result_text = data["candidates"][0]["content"]["parts"][0]["text"]

                    # Parse JSON
                    import json
                    result = json.loads(result_text.strip().strip('`').strip())

                    is_legal = result.get("is_legal", False)
                    confidence = float(result.get("confidence", 0.5))

                    return {
                        "is_legal": is_legal,
                        "confidence": confidence,
                        "suggested_workflow": "ursall" if is_legal else "standard"
                    }

    except Exception as e:
        logger.error(f"Quick document check failed: {e}")

    # Fallback
    return {
        "is_legal": False,
        "confidence": 0.0,
        "suggested_workflow": "standard"
    }


def is_gemini_available() -> bool:
    """Check if Gemini is available for summarization"""
    return GEMINI_AVAILABLE
