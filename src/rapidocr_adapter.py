"""Patched copy of ocr_processor.py with RapidOCR integration"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import cv2
import numpy as np
from typing import List, Dict, Optional, Any
from PIL import Image

import config
from logger import get_logger

logger = get_logger(__name__)


class RapidOCRAdapter:
    """Adapter for RapidOCR to match existing OCR interface"""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self.reader = None

    def initialize(self):
        """Initialize RapidOCR reader"""
        try:
            from rapidocr_onnxruntime import RapidOCR as _RapidOCR

            self.reader = _RapidOCR()
            logger.info("RapidOCR initialized successfully")
            return True
        except ImportError:
            logger.error(
                "RapidOCR not installed. Install with: pip install rapidocr-onnxruntime"
            )
            return False

    def process_image(self, image: np.ndarray) -> List[Dict]:
        """Process image and return text results"""
        if self.reader is None:
            if not self.initialize():
                return []

        try:
            # RapidOCR returns: [[points, (text, confidence)], ...]
            result = self.reader(image)

            texts = []
            if result and result[0]:
                for item in result[0]:
                    points, (text, confidence) = item

                    # Calculate bounding box
                    x_coords = [p[0] for p in points]
                    y_coords = [p[1] for p in points]

                    x_min = int(min(x_coords))
                    y_min = int(min(y_coords))
                    x_max = int(max(x_coords))
                    y_max = int(max(y_coords))

                    width = x_max - x_min
                    height = y_max - y_min

                    # Estimate font size from height
                    font_size = int(height * 0.75)

                    texts.append(
                        {
                            "text": text,
                            "confidence": float(confidence),
                            "bbox": (x_min, y_min, width, height),
                            "font_size": font_size,
                            "text_width": width,
                            "alignment": "left",
                            "y_position": y_min,
                            "text_region": None,
                            "layout_info": {"page_index": 1, "column_index": 1},
                            "position": points,
                        }
                    )

            return texts

        except Exception as e:
            logger.error(f"Error processing image with RapidOCR: {e}")
            return []


# Create test script
if __name__ == "__main__":
    import sys

    ocr = RapidOCRAdapter(lang="en")

    if not ocr.initialize():
        sys.exit(1)

    # Test on first image
    test_image = Path(__file__).parent.parent / "testcases" / "HIPPO_20220124_0004.jpg"
    if not test_image.exists():
        print(f"Test image not found: {test_image}")
        sys.exit(1)

    img = cv2.imread(str(test_image))
    if img is None:
        print(f"Could not load image: {test_image}")
        sys.exit(1)

    print(f"Testing RapidOCR on {test_image.name}...")
    results = ocr.process_image(img)

    print(f"\nDetected {len(results)} text regions:")
    for i, text_info in enumerate(results[:10], 1):
        text = text_info.get("text", "")
        conf = text_info.get("confidence", 0)
        print(f"  {i}. [{conf:.2f}] {text}")
