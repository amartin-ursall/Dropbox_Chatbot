"""
Dolphin Parser Wrapper
Integrates Dolphin document parsing capabilities into the application
"""

import logging
import os
import sys
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add Dolphin directory to path
DOLPHIN_PATH = Path(__file__).parent.parent / "Dolphin"
sys.path.insert(0, str(DOLPHIN_PATH))

try:
    from omegaconf import OmegaConf
    from PIL import Image
    from chat import DOLPHIN
    from utils.utils import (
        convert_pdf_to_images,
        prepare_image,
        parse_layout_string,
        process_coordinates
    )
    import cv2
    DOLPHIN_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Dolphin dependencies not available: {e}")
    DOLPHIN_AVAILABLE = False

logger = logging.getLogger(__name__)


class DolphinParser:
    """Wrapper class for Dolphin document parsing"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Dolphin parser

        Args:
            config_path: Path to Dolphin config file. If None, uses default.
        """
        if not DOLPHIN_AVAILABLE:
            raise RuntimeError("Dolphin dependencies are not installed")

        if config_path is None:
            config_path = str(DOLPHIN_PATH / "config" / "Dolphin.yaml")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Dolphin config not found at {config_path}")

        logger.info(f"Loading Dolphin model from config: {config_path}")
        self.config = OmegaConf.load(config_path)

        # Fix relative paths in config to absolute paths
        dolphin_dir = Path(config_path).parent.parent
        if not Path(self.config.model.model_name_or_path).is_absolute():
            self.config.model.model_name_or_path = str(dolphin_dir / self.config.model.model_name_or_path)
        if not Path(self.config.model.tokenizer_path).is_absolute():
            self.config.model.tokenizer_path = str(dolphin_dir / self.config.model.tokenizer_path)

        logger.info(f"Model path: {self.config.model.model_name_or_path}")
        logger.info(f"Tokenizer path: {self.config.model.tokenizer_path}")

        self.model = DOLPHIN(self.config)
        logger.info("Dolphin model loaded successfully")

    def parse_document(
        self,
        document_path: str,
        max_batch_size: int = 4
    ) -> Tuple[Dict, float]:
        """
        Parse a document (image or PDF) and extract structured content

        Args:
            document_path: Path to document file (PDF, JPG, PNG)
            max_batch_size: Max batch size for parallel processing

        Returns:
            Tuple of (parsed_content, confidence_score)
            - parsed_content: Dict with structure:
                {
                    "text": str,  # Full extracted text
                    "elements": List[Dict],  # All elements with labels
                    "pages": int,  # Number of pages (1 for images)
                    "has_tables": bool,
                    "has_figures": bool
                }
            - confidence_score: Average confidence (0-1)
        """
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found: {document_path}")

        file_ext = os.path.splitext(document_path)[1].lower()

        if file_ext == '.pdf':
            return self._parse_pdf(document_path, max_batch_size)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            return self._parse_image(document_path, max_batch_size)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    def _parse_image(
        self,
        image_path: str,
        max_batch_size: int
    ) -> Tuple[Dict, float]:
        """Parse a single image file"""
        logger.info(f"Parsing image: {image_path}")

        pil_image = Image.open(image_path).convert("RGB")
        elements, confidence = self._process_single_image(pil_image, max_batch_size)

        # Build structured content
        content = self._build_content_dict(elements, num_pages=1)

        return content, confidence

    def _parse_pdf(
        self,
        pdf_path: str,
        max_batch_size: int
    ) -> Tuple[Dict, float]:
        """Parse a PDF file (multi-page support)"""
        logger.info(f"Parsing PDF: {pdf_path}")

        # Convert PDF to images
        images = convert_pdf_to_images(pdf_path)
        if not images:
            raise Exception(f"Failed to convert PDF {pdf_path} to images")

        all_elements = []
        all_confidences = []

        # Process each page
        for page_idx, pil_image in enumerate(images):
            logger.info(f"Processing page {page_idx + 1}/{len(images)}")

            elements, confidence = self._process_single_image(pil_image, max_batch_size)

            # Add page number to each element
            for elem in elements:
                elem['page'] = page_idx + 1

            all_elements.extend(elements)
            all_confidences.append(confidence)

        # Calculate average confidence
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

        # Build structured content
        content = self._build_content_dict(all_elements, num_pages=len(images))

        return content, avg_confidence

    def _process_single_image(
        self,
        image: Image.Image,
        max_batch_size: int
    ) -> Tuple[List[Dict], float]:
        """
        Process a single image and extract elements

        Returns:
            Tuple of (elements_list, confidence_score)
        """
        # Stage 1: Page-level layout and reading order parsing
        layout_output = self.model.chat("Parse the reading order of this document.", image)

        # Stage 2: Element-level content parsing
        padded_image, dims = prepare_image(image)
        elements = self._process_elements(layout_output, padded_image, dims, max_batch_size)

        # Calculate confidence (placeholder - Dolphin doesn't return explicit scores by default)
        # In production, you could enhance this by analyzing output quality
        confidence = 0.85  # Default confidence

        return elements, confidence

    def _process_elements(
        self,
        layout_results: str,
        padded_image,
        dims,
        max_batch_size: int
    ) -> List[Dict]:
        """Parse all document elements with parallel decoding"""
        layout_results = parse_layout_string(layout_results)

        text_table_elements = []  # Elements that need processing
        figure_results = []  # Figure elements (no processing needed)
        previous_box = None
        reading_order = 0

        # Collect elements for processing
        for bbox, label in layout_results:
            try:
                # Adjust coordinates
                x1, y1, x2, y2, orig_x1, orig_y1, orig_x2, orig_y2, previous_box = process_coordinates(
                    bbox, padded_image, dims, previous_box
                )

                # Crop and parse element
                cropped = padded_image[y1:y2, x1:x2]
                if cropped.size > 0 and cropped.shape[0] > 3 and cropped.shape[1] > 3:
                    if label == "fig":
                        # For figures, just note their presence
                        figure_results.append({
                            "label": label,
                            "text": "[Figure]",
                            "bbox": [orig_x1, orig_y1, orig_x2, orig_y2],
                            "reading_order": reading_order,
                        })
                    else:
                        # For text or table regions, prepare for parsing
                        pil_crop = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
                        prompt = "Parse the table in the image." if label == "tab" else "Read text in the image."
                        text_table_elements.append({
                            "crop": pil_crop,
                            "prompt": prompt,
                            "label": label,
                            "bbox": [orig_x1, orig_y1, orig_x2, orig_y2],
                            "reading_order": reading_order,
                        })

                reading_order += 1

            except Exception as e:
                logger.warning(f"Error processing bbox with label {label}: {str(e)}")
                continue

        # Parse text/table elements in parallel
        recognition_results = figure_results
        if text_table_elements:
            crops_list = [elem["crop"] for elem in text_table_elements]
            prompts_list = [elem["prompt"] for elem in text_table_elements]

            # Inference in batch
            batch_results = self.model.chat(prompts_list, crops_list, max_batch_size=max_batch_size)

            # Add batch results to recognition_results
            for i, result in enumerate(batch_results):
                elem = text_table_elements[i]
                recognition_results.append({
                    "label": elem["label"],
                    "bbox": elem["bbox"],
                    "text": result.strip(),
                    "reading_order": elem["reading_order"],
                })

        # Sort elements by reading order
        recognition_results.sort(key=lambda x: x.get("reading_order", 0))

        return recognition_results

    def _build_content_dict(self, elements: List[Dict], num_pages: int) -> Dict:
        """Build structured content dictionary from elements"""

        # Extract full text in reading order
        full_text = "\n\n".join([
            elem['text'] for elem in elements
            if elem['text'] and elem['text'] != "[Figure]"
        ])

        # Detect content types
        has_tables = any(elem['label'] == 'tab' for elem in elements)
        has_figures = any(elem['label'] == 'fig' for elem in elements)

        return {
            "text": full_text,
            "elements": elements,
            "pages": num_pages,
            "has_tables": has_tables,
            "has_figures": has_figures
        }


def is_dolphin_available() -> bool:
    """Check if Dolphin is available"""
    return DOLPHIN_AVAILABLE


def get_dolphin_parser() -> Optional[DolphinParser]:
    """
    Get a Dolphin parser instance if available

    Returns:
        DolphinParser instance or None if not available
    """
    if not DOLPHIN_AVAILABLE:
        logger.warning("Dolphin is not available")
        return None

    try:
        return DolphinParser()
    except Exception as e:
        logger.error(f"Failed to initialize Dolphin parser: {e}")
        return None
