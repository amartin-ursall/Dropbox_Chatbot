"""
Document Preview Service
Orchestrates Dolphin parsing + Gemini summarization to create document previews
"""

import logging
import os
from typing import Dict, Optional, Tuple
from pathlib import Path

from app.dolphin_parser import get_dolphin_parser, is_dolphin_available
from app.gemini_summarizer import (
    summarize_document,
    quick_document_check,
    is_gemini_available
)

logger = logging.getLogger(__name__)


class DocumentPreviewService:
    """Service for generating document previews"""

    def __init__(self):
        """Initialize the preview service"""
        self.dolphin_available = is_dolphin_available()
        self.gemini_available = is_gemini_available()

        logger.info(f"DocumentPreviewService initialized - Dolphin: {self.dolphin_available}, Gemini: {self.gemini_available}")

        # Initialize Dolphin parser if available
        self.dolphin_parser = None
        if self.dolphin_available:
            try:
                self.dolphin_parser = get_dolphin_parser()
                if self.dolphin_parser:
                    logger.info("Dolphin parser loaded successfully")
                else:
                    logger.warning("Dolphin parser initialization returned None")
                    self.dolphin_available = False
            except Exception as e:
                logger.error(f"Failed to initialize Dolphin parser: {e}")
                self.dolphin_available = False

    async def generate_preview(
        self,
        file_path: str,
        file_id: str,
        target_use: str = "legal"
    ) -> Dict:
        """
        Generate a complete document preview

        Args:
            file_path: Path to uploaded document
            file_id: Unique file identifier
            target_use: "legal" for URSALL or "general" for standard workflow

        Returns:
            Dict with structure:
            {
                "file_id": str,
                "status": "success" or "error",
                "preview": {
                    "summary": str,
                    "document_type": str,
                    "confidence": float,
                    "is_legal_document": bool,
                    "pages": int,
                    "has_tables": bool,
                    "has_figures": bool,
                    "suggested_workflow": "ursall" or "standard",
                    "key_information": Dict,
                    "suggested_answers": Dict
                },
                "raw_text": str,  # Full extracted text (optional)
                "error": str or None
            }
        """
        try:
            # Step 1: Check file exists
            if not os.path.exists(file_path):
                return self._error_response(file_id, f"File not found: {file_path}")

            logger.info(f"Starting document preview for file: {file_path}")

            # Step 2: Parse document with Dolphin (if available) or fallback to PyMuPDF
            if self.dolphin_available and self.dolphin_parser:
                try:
                    logger.info("Attempting to parse with Dolphin")
                    parsed_content, parse_confidence = self.dolphin_parser.parse_document(file_path)

                    # Extract metadata
                    metadata = {
                        "pages": parsed_content.get("pages", 1),
                        "has_tables": parsed_content.get("has_tables", False),
                        "has_figures": parsed_content.get("has_figures", False)
                    }

                    document_text = parsed_content.get("text", "")
                    logger.info(f"Dolphin parsing successful: {len(document_text)} characters extracted")
                except Exception as e:
                    logger.warning(f"Dolphin parsing failed: {e}")
                    logger.info("Falling back to PyMuPDF + Gemini")
                    document_text, metadata, parse_confidence = self._extract_text_pymupdf(file_path)
            else:
                # Fallback: Extract text using PyMuPDF directly (without Dolphin)
                logger.info("Dolphin not available, using PyMuPDF for text extraction")
                document_text, metadata, parse_confidence = self._extract_text_pymupdf(file_path)

            if not document_text or len(document_text.strip()) == 0:
                return self._error_response(file_id, "No se pudo extraer texto del documento")

            # Step 3: Quick check if Gemini is not available
            if not self.gemini_available:
                logger.warning("Gemini not available - returning basic preview")
                return self._basic_preview(file_id, document_text, metadata, parse_confidence)

            # Step 4: Summarize with Gemini
            try:
                summary_result = await summarize_document(document_text, metadata, target_use)

                if not summary_result:
                    logger.warning("Gemini summarization returned None - using basic preview")
                    return self._basic_preview(file_id, document_text, metadata, parse_confidence)

            except Exception as e:
                logger.error(f"Gemini summarization failed: {e}")
                return self._basic_preview(file_id, document_text, metadata, parse_confidence)

            # Step 5: Determine suggested workflow
            is_legal = summary_result.get("is_legal_document", False)
            suggested_workflow = "ursall" if is_legal else "standard"

            # Build complete preview
            preview = {
                "summary": summary_result.get("summary", "Documento procesado correctamente"),
                "document_type": summary_result.get("document_type", "documento"),
                "confidence": summary_result.get("confidence", parse_confidence),
                "is_legal_document": is_legal,
                "pages": metadata["pages"],
                "has_tables": metadata["has_tables"],
                "has_figures": metadata["has_figures"],
                "suggested_workflow": suggested_workflow,
                "key_information": summary_result.get("key_information", {}),
                "suggested_answers": summary_result.get("suggested_answers", {})
            }

            logger.info(f"Preview generated successfully for {file_id}: {preview['document_type']}")

            return {
                "file_id": file_id,
                "status": "success",
                "preview": preview,
                "raw_text": document_text[:500],  # First 500 chars for verification
                "error": None
            }

        except Exception as e:
            logger.error(f"Unexpected error in generate_preview: {e}", exc_info=True)
            return self._error_response(file_id, f"Unexpected error: {str(e)}")

    def _extract_text_pymupdf(self, file_path: str) -> Tuple[str, Dict, float]:
        """
        Extract text from PDF using PyMuPDF as fallback

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (text, metadata, confidence)
        """
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            text_parts = []

            for page in doc:
                text_parts.append(page.get_text())

            full_text = "\n\n".join(text_parts)

            metadata = {
                "pages": len(doc),
                "has_tables": False,  # PyMuPDF doesn't detect tables automatically
                "has_figures": False
            }

            doc.close()

            return full_text, metadata, 0.7  # Lower confidence than Dolphin

        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            return "", {"pages": 1, "has_tables": False, "has_figures": False}, 0.0

    def _basic_preview(
        self,
        file_id: str,
        document_text: str,
        metadata: Dict,
        confidence: float
    ) -> Dict:
        """
        Generate basic preview when Gemini is not available

        Args:
            file_id: File identifier
            document_text: Extracted text
            metadata: Document metadata
            confidence: Parse confidence score

        Returns:
            Basic preview dict
        """
        preview = {
            "summary": "Documento procesado correctamente. Análisis inteligente no disponible.",
            "document_type": "documento",
            "confidence": confidence,
            "is_legal_document": False,
            "pages": metadata["pages"],
            "has_tables": metadata["has_tables"],
            "has_figures": metadata["has_figures"],
            "suggested_workflow": "standard",
            "key_information": {},
            "suggested_answers": {}
        }

        return {
            "file_id": file_id,
            "status": "success",
            "preview": preview,
            "raw_text": document_text[:500],
            "error": None
        }

    def _error_response(self, file_id: str, error_message: str) -> Dict:
        """Generate error response"""
        return {
            "file_id": file_id,
            "status": "error",
            "preview": None,
            "raw_text": None,
            "error": error_message
        }

    def get_status(self) -> Dict:
        """
        Get service status

        Returns:
            Dict with service availability status
        """
        return {
            "dolphin_available": self.dolphin_available,
            "gemini_available": self.gemini_available,
            "preview_available": self.dolphin_available and self.gemini_available,
            "message": self._get_status_message()
        }

    def _get_status_message(self) -> str:
        """Get human-readable status message"""
        if self.dolphin_available and self.gemini_available:
            return "Document preview service fully operational"
        elif self.dolphin_available:
            return "Document preview available with basic parsing (Gemini unavailable)"
        elif self.gemini_available:
            return "Document preview unavailable (Dolphin parser not configured)"
        else:
            return "Document preview unavailable (both Dolphin and Gemini not configured)"


# Global service instance
_preview_service: Optional[DocumentPreviewService] = None


def get_preview_service() -> DocumentPreviewService:
    """
    Get or create the global preview service instance

    Returns:
        DocumentPreviewService instance
    """
    global _preview_service

    if _preview_service is None:
        _preview_service = DocumentPreviewService()

    return _preview_service


async def generate_document_preview(
    file_path: str,
    file_id: str,
    target_use: str = "legal"
) -> Dict:
    """
    Convenience function to generate document preview

    Args:
        file_path: Path to document
        file_id: Unique file ID
        target_use: "legal" or "general"

    Returns:
        Preview dictionary
    """
    service = get_preview_service()
    return await service.generate_preview(file_path, file_id, target_use)


def check_preview_availability() -> Dict:
    """
    Check if preview service is available

    Returns:
        Status dictionary
    """
    service = get_preview_service()
    return service.get_status()
