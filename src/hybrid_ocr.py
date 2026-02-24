"""Hybrid OCR processor supporting both PDF and image inputs

This module provides intelligent OCR routing:
- PDF files: Uses PyMuPDF4LLM for high-accuracy text extraction with style preservation
- Image files: Uses Tesseract-based OCR for scanned images
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Union
import re

from PIL import Image

import sys

sys.path.insert(0, str(Path(__file__).parent))

import config
from logger import get_logger

logger = get_logger(__name__)


class HybridOCR:
    def __init__(self, tesseract_lang: str = None):
        """Initialize hybrid OCR processor.

        Args:
            tesseract_lang: Language for image OCR (default from config)
        """
        self.tesseract_lang = tesseract_lang or config.OCR_LANGUAGE

        self.pymupdf4llm_available = False
        self.ocr_processor = None

        self._try_load_pymupdf4llm()
        self._load_tesseract_ocr()

    def _try_load_pymupdf4llm(self):
        try:
            import pymupdf4llm

            self.pymupdf4llm_available = True
        except ImportError:
            if config.USE_HYBRID_OCR:
                logger.warning(
                    "PyMuPDF4LLM not available. "
                    "PDF files will be processed as images. "
                    "Install: pip install pymupdf4llm"
                )

    def _load_tesseract_ocr(self):
        try:
            from ocr_processor import BookletOCR

            self.ocr_processor = BookletOCR(
                lang=self.tesseract_lang, use_gpu=config.OCR_USE_GPU
            )
        except Exception as e:
            logger.error(f"Error loading Tesseract OCR: {e}")

    def detect_input_type(self, path: Union[str, Path]) -> str:
        path = Path(path)
        ext = path.suffix.lower()

        if ext == ".pdf":
            return "pdf"
        elif ext in {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}:
            return "image"
        elif path.is_dir():
            return "directory"
        else:
            return "unknown"

    def process_file(self, file_path: Union[str, Path]) -> Dict:
        input_type = self.detect_input_type(file_path)

        if input_type == "pdf":
            return self._process_pdf(file_path)
        elif input_type == "image":
            return self._process_image(file_path)
        else:
            return {
                "success": False,
                "error": f"Unsupported file type or directory: {file_path}",
            }

    def process_directory(self, dir_path: Union[str, Path]) -> List[Dict]:
        images_data = []
        from image_utils import get_image_files, load_image

        image_files = get_image_files(dir_path)

        for img_path in image_files:
            img = load_image(img_path)
            if img is None:
                images_data.append(
                    {"image_path": str(img_path), "error": "Failed to load"}
                )
                continue

            try:
                result = self._process_image(img_path)
                result["image_path"] = str(img_path)
                images_data.append(result)
            except Exception as e:
                images_data.append({"image_path": str(img_path), "error": str(e)})

        return images_data

    def _process_pdf(self, pdf_path: Union[str, Path]) -> Dict:
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            return {"success": False, "error": f"PDF not found: {pdf_path}"}

        if self.pymupdf4llm_available and config.USE_HYBRID_OCR:
            try:
                import pymupdf4llm

                markdown_text = pymupdf4llm.to_markdown(str(pdf_path))

                pages_data = self._parse_pdf_markdown(markdown_text)

                return {
                    "success": True,
                    "type": "pdf",
                    "source": str(pdf_path),
                    "pages": pages_data,
                    "num_pages": len(pages_data),
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"PyMuPDF4LLM processing failed: {e}",
                }
        else:
            return {
                "success": False,
                "error": (
                    "PDF support requires PyMuPDF4LLM. "
                    "Install: pip install pymupdf4llm or process PDF as images"
                ),
            }

    def _process_image(self, image_path: Union[str, Path]) -> Dict:
        image_path = Path(image_path)

        if not image_path.exists():
            return {"success": False, "error": f"Image not found: {image_path}"}

        if self.ocr_processor is None:
            return {"success": False, "error": "Tesseract OCR not available"}

        try:
            image = load_image(image_path)

            if image is None:
                return {"success": False, "error": "Failed to load image"}

            ocr_results = self.ocr_processor.process_image(image)
            grouped_results = self.ocr_processor.group_text_lines(
                ocr_results, y_threshold=getattr(config, "Y_GROUP_THRESHOLD", 15)
            )

            for text_info in grouped_results:
                text_info["styles"] = self.ocr_processor.classify_text_style(
                    text_info,
                    min_heading_size=getattr(config, "MIN_HEADING_FONT_SIZE", 24),
                )

            return {
                "success": True,
                "type": "image",
                "source": str(image_path),
                "results": grouped_results,
                "num_texts": len(grouped_results),
            }

        except Exception as e:
            return {"success": False, "error": f"Image processing failed: {e}"}

    def _parse_pdf_markdown(self, markdown_text: str) -> List[Dict]:
        if not markdown_text:
            return []

        pages = []
        current_page = []

        lines = markdown_text.split("\n")

        for line in lines:
            if "---" in line and len(current_page) > 0:
                pages.append({"content": current_page, "type": "markdown"})
                current_page = []
            else:
                current_page.append(line)

        if current_page:
            pages.append({"content": current_page, "type": "markdown"})

        if not pages:
            pages.append({"content": lines, "type": "markdown"})

        return pages


def process_any_input(
    input_path: Union[str, Path],
) -> Dict:
    processed_data = None
    content_type = None

    path = Path(input_path)

    if path.is_dir():
        hybrid = HybridOCR()
        processed_data = hybrid.process_directory(input_path)
        content_type = "directory"
    elif path.is_file():
        hybrid = HybridOCR()
        processed_data = hybrid.process_file(input_path)
        content_type = Path(input_path).suffix.lower()
    else:
        return {
            "success": False,
            "error": f"Input not found: {input_path}",
        }

    return {
        "success": True,
        "type": content_type,
        "data": processed_data,
        "source": str(input_path),
    }
