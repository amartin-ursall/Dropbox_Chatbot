"""
Dolphin REST API Client
Connects to Dolphin Document Parsing API service for document processing
"""
import os
import logging
import httpx
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Get Dolphin API configuration
DOLPHIN_API_URL = os.getenv("DOLPHIN_API_URL", "http://192.168.0.98:1000")
DOLPHIN_API_TIMEOUT = int(os.getenv("DOLPHIN_API_TIMEOUT", "60"))  # seconds
DOLPHIN_AVAILABLE = True  # REST API doesn't need local dependencies

logger.info(f"Dolphin REST API configured at: {DOLPHIN_API_URL}")


class DolphinRestClient:
    """REST API client for Dolphin document parsing service"""

    def __init__(self, api_url: Optional[str] = None, timeout: int = 60):
        """
        Initialize Dolphin REST client

        Args:
            api_url: Base URL of Dolphin API (default: from env or 192.168.0.98:1000)
            timeout: Request timeout in seconds (default: 60)
        """
        self.api_url = api_url or DOLPHIN_API_URL
        self.timeout = timeout
        logger.info(f"Initialized DolphinRestClient with URL: {self.api_url}")

    async def check_health(self) -> Dict:
        """
        Check if Dolphin API service is healthy

        Returns:
            Dict with health status:
            {
                "status": "healthy",
                "model_loaded": True,
                "device": "cpu"
            }

        Raises:
            Exception: If service is not available
        """
        url = f"{self.api_url}/health"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)

                if response.status_code != 200:
                    raise Exception(f"Health check failed with status {response.status_code}")

                data = response.json()
                logger.info(f"Dolphin API health check: {data}")
                return data

        except httpx.ConnectError:
            logger.error(f"Cannot connect to Dolphin API at {self.api_url}")
            raise Exception(f"Dolphin API is not reachable at {self.api_url}")
        except Exception as e:
            logger.error(f"Dolphin API health check failed: {e}")
            raise

    async def parse_document(
        self,
        document_path: str,
        max_batch_size: int = 16
    ) -> Tuple[Dict, float]:
        """
        Parse a document (image or PDF) using Dolphin API

        Args:
            document_path: Path to document file (PDF, JPG, PNG, JPEG)
            max_batch_size: Max batch size for parallel processing (default: 16)

        Returns:
            Tuple of (parsed_content, confidence_score)
            - parsed_content: Dict with structure:
                {
                    "text": str,  # Full extracted text
                    "elements": List[Dict],  # All elements with labels
                    "pages": int,  # Number of pages (1 for images)
                    "has_tables": bool,
                    "has_figures": bool,
                    "file_type": str  # "image" or "pdf"
                }
            - confidence_score: Average confidence (0-1)

        Raises:
            FileNotFoundError: If document doesn't exist
            Exception: If API request fails
        """
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found: {document_path}")

        # Validate file type
        file_ext = os.path.splitext(document_path)[1].lower()
        if file_ext not in ['.pdf', '.jpg', '.jpeg', '.png']:
            raise ValueError(f"Unsupported file type: {file_ext}. Supported: PDF, JPG, JPEG, PNG")

        logger.info(f"Parsing document via Dolphin API: {document_path}")

        url = f"{self.api_url}/parse"

        try:
            # Prepare multipart form data
            with open(document_path, 'rb') as f:
                files = {'file': (os.path.basename(document_path), f, self._get_mime_type(file_ext))}
                data = {'max_batch_size': max_batch_size}

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, files=files, data=data)

                    if response.status_code != 200:
                        error_detail = response.text
                        logger.error(f"Dolphin API error {response.status_code}: {error_detail}")
                        raise Exception(f"Dolphin API returned error {response.status_code}: {error_detail}")

                    result = response.json()

                    if not result.get("success"):
                        raise Exception("Dolphin API parsing failed")

                    # Process response based on file type
                    parsed_content = self._process_api_response(result)
                    confidence = self._calculate_confidence(result)

                    logger.info(f"Successfully parsed document: {result.get('file_type')}, "
                               f"pages: {parsed_content['pages']}, elements: {len(parsed_content['elements'])}")

                    return parsed_content, confidence

        except httpx.TimeoutException:
            logger.error(f"Dolphin API request timed out after {self.timeout}s")
            raise Exception(f"Document parsing timed out after {self.timeout} seconds")
        except httpx.ConnectError:
            logger.error(f"Cannot connect to Dolphin API at {self.api_url}")
            raise Exception(f"Dolphin API is not reachable at {self.api_url}")
        except Exception as e:
            logger.error(f"Dolphin API parsing error: {e}", exc_info=True)
            raise

    def _get_mime_type(self, file_ext: str) -> str:
        """Get MIME type for file extension"""
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        return mime_types.get(file_ext.lower(), 'application/octet-stream')

    def _process_api_response(self, result: Dict) -> Dict:
        """
        Process API response into unified format

        Args:
            result: Raw API response

        Returns:
            Structured content dict
        """
        file_type = result.get("file_type", "unknown")

        if file_type == "image":
            # Image response format
            elements = result.get("results", [])
            num_pages = 1
        elif file_type == "pdf":
            # PDF response format
            num_pages = result.get("total_pages", 0)
            # Flatten elements from all pages
            elements = []
            for page_result in result.get("results", []):
                page_num = page_result.get("page_number", 1)
                page_elements = page_result.get("elements", [])
                # Add page number to each element
                for elem in page_elements:
                    elem['page'] = page_num
                elements.extend(page_elements)
        else:
            raise Exception(f"Unknown file type from API: {file_type}")

        # Extract full text in reading order
        full_text = self._extract_text(elements)

        # Detect content types
        has_tables = any(elem.get('label') == 'tab' for elem in elements)
        has_figures = any(elem.get('label') == 'fig' for elem in elements)

        return {
            "text": full_text,
            "elements": elements,
            "pages": num_pages,
            "has_tables": has_tables,
            "has_figures": has_figures,
            "file_type": file_type
        }

    def _extract_text(self, elements: List[Dict]) -> str:
        """
        Extract full text from elements in reading order

        Args:
            elements: List of parsed elements

        Returns:
            Full text string
        """
        # Sort by reading order if available
        sorted_elements = sorted(elements, key=lambda x: x.get("reading_order", 0))

        # Extract text, skipping figures
        text_parts = []
        for elem in sorted_elements:
            text = elem.get('text', '')
            if text and text != "[Figure]":
                text_parts.append(text)

        return "\n\n".join(text_parts)

    def _calculate_confidence(self, result: Dict) -> float:
        """
        Calculate confidence score from API response

        Currently returns a default confidence as Dolphin API doesn't
        return explicit confidence scores.

        Args:
            result: API response

        Returns:
            Confidence score (0-1)
        """
        # Check if parsing was successful
        if not result.get("success"):
            return 0.0

        # Check if we got results
        file_type = result.get("file_type")
        if file_type == "image":
            has_results = len(result.get("results", [])) > 0
        elif file_type == "pdf":
            has_results = result.get("total_pages", 0) > 0
        else:
            has_results = False

        # Return default confidence
        return 0.85 if has_results else 0.0


def is_dolphin_api_available() -> bool:
    """Check if Dolphin REST API is configured"""
    return DOLPHIN_AVAILABLE


async def get_dolphin_rest_client() -> Optional[DolphinRestClient]:
    """
    Get a Dolphin REST client instance and verify it's reachable

    Returns:
        DolphinRestClient instance or None if not available

    Raises:
        Exception: If client initialization fails
    """
    if not DOLPHIN_AVAILABLE:
        logger.warning("Dolphin REST API is not available")
        return None

    try:
        client = DolphinRestClient()
        # Verify API is reachable
        await client.check_health()
        logger.info("Dolphin REST API client ready")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Dolphin REST client: {e}")
        raise


async def check_dolphin_api_status() -> Dict:
    """
    Check Dolphin API status

    Returns:
        Dict with status information
    """
    try:
        client = DolphinRestClient()
        health = await client.check_health()
        return {
            "available": True,
            "api_url": client.api_url,
            "health": health,
            "error": None
        }
    except Exception as e:
        return {
            "available": False,
            "api_url": DOLPHIN_API_URL,
            "health": None,
            "error": str(e)
        }
