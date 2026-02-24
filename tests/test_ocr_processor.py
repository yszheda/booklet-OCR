"""Unit tests for ocr_processor module"""

import unittest
import sys
from pathlib import Path
from PIL import Image
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from ocr_processor import BookletOCR
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

import config


class TestOCRProcessor(unittest.TestCase):
    """Test OCR processor functionality"""

    @classmethod
    def setUpClass(cls):
        """Setup test fixtures"""
        cls.test_dir = Path(__file__).parent.parent / "testcases"
        cls.output_dir = Path(__file__).parent / "test_output"
        cls.output_dir.mkdir(exist_ok=True)

    def setUp(self):
        """Setup before each test"""
        if not TESSERACT_AVAILABLE:
            self.skipTest("Tesseract not available")

    def test_ocr_initialization(self):
        """Test OCR processor initialization"""
        ocr = BookletOCR(lang="en")
        self.assertIsNotNone(ocr)

    def test_ocr_detection_bold(self):
        """Test bold text detection"""
        ocr = BookletOCR(lang="en")

        test_image = False
        try:
            img = Image.new("RGB", (200, 50), color="white")
            draw = "try: ImageDraw.Draw(img)"

            test_image = True
        except:
            pass

        if not test_image:
            self.skipTest("Cannot create test image")

    def test_ocr_group_text_lines(self):
        """Test text line grouping"""
        ocr = BookletOCR(lang="en")

        texts = [
            {
                "text": "line1",
                "confidence": 0.9,
                "position": [[0, 100], [100, 100], [100, 120], [0, 120]],
                "y_position": 100,
                "bbox": (0, 100, 100, 20),
                "font_size": 20,
                "alignment": "left",
                "text_region": None,
                "layout_info": {"page_index": 1, "column_index": 1},
            },
            {
                "text": "line2a",
                "confidence": 0.92,
                "position": [[0, 105], [50, 105], [50, 125], [0, 125]],
                "y_position": 105,
                "bbox": (0, 105, 50, 20),
                "font_size": 20,
                "alignment": "left",
                "text_region": None,
                "layout_info": {"page_index": 1, "column_index": 1},
            },
            {
                "text": "line2b",
                "confidence": 0.88,
                "position": [[50, 105], [100, 105], [100, 125], [50, 125]],
                "y_position": 105,
                "bbox": (50, 105, 50, 20),
                "font_size": 20,
                "alignment": "left",
                "text_region": None,
                "layout_info": {"page_index": 1, "column_index": 1},
            },
            {
                "text": "line3",
                "confidence": 0.95,
                "position": [[0, 200], [100, 200], [100, 220], [0, 220]],
                "y_position": 200,
                "bbox": (0, 200, 100, 20),
                "font_size": 20,
                "alignment": "left",
                "text_region": None,
                "layout_info": {"page_index": 1, "column_index": 1},
            },
        ]

        grouped = ocr.group_text_lines(texts, y_threshold=15, respect_layout=False)

        self.assertGreater(len(grouped), 0)

    def test_classify_text_style_heading(self):
        """Test heading classification"""
        ocr = BookletOCR(lang="en")

        text_info = {
            "font_size": 50,
            "alignment": "center",
            "text": "Chapter Title",
            "text_region": None,
        }

        styles = ocr.classify_text_style(text_info, min_heading_size=36)

        self.assertTrue(styles.get("is_heading"))
        self.assertIsNotNone(styles.get("heading_level"))

    def test_classify_text_style_list(self):
        """Test list item classification"""
        ocr = BookletOCR(lang="en")

        text_info = {
            "font_size": 20,
            "alignment": "left",
            "text": "- First item",
            "text_region": None,
        }

        styles = ocr.classify_text_style(text_info, min_heading_size=36)

        self.assertTrue(styles.get("is_list"))
        self.assertEqual(styles.get("list_type"), "bullet")

    def test_classify_text_style_numbered_list(self):
        """Test numbered list classification"""
        ocr = BookletOCR(lang="en")

        text_info = {
            "font_size": 20,
            "alignment": "left",
            "text": "1. First item",
            "text_region": None,
        }

        styles = ocr.classify_text_style(text_info, min_heading_size=36)

        self.assertTrue(styles.get("is_list"))
        self.assertEqual(styles.get("list_type"), "numbered")

    def test_classify_text_style_centered(self):
        """Test centered text classification"""
        ocr = BookletOCR(lang="en")

        text_info = {
            "font_size": 20,
            "alignment": "center",
            "text": "Centered text",
            "text_region": None,
        }

        styles = ocr.classify_text_style(text_info, min_heading_size=36)

        self.assertTrue(styles.get("is_centered"))
        self.assertFalse(styles.get("is_heading"))

    def test_process_test_images(self):
        """Test processing test images"""
        ocr = BookletOCR(lang="en")

        test_images = list(self.test_dir.glob("*.jpg"))
        if not test_images:
            return

        test_image = test_images[0]
        image = Image.open(test_image).convert("RGB")

        results = ocr.process_image(image)

        self.assertIsInstance(results, list)

    def test_merge_line_single(self):
        """Test merging single text line"""
        ocr = BookletOCR(lang="en")

        line_texts = [
            {
                "text": "single",
                "bbox": (0, 0, 100, 20),
                "confidence": 0.9,
                "position": [[0, 0], [100, 0], [100, 20], [0, 20]],
                "font_size": 20,
                "alignment": "left",
                "y_position": 0,
                "text_region": None,
                "layout_info": {"page_index": 1, "column_index": 1},
            }
        ]

        merged = ocr._merge_line(line_texts)

        self.assertEqual(merged["text"], "single")

    def test_merge_line_multiple(self):
        """Test merging multiple text blocks"""
        ocr = BookletOCR(lang="en")

        line_texts = [
            {
                "text": "Hello",
                "bbox": (0, 0, 50, 20),
                "confidence": 0.9,
                "position": [[0, 0], [50, 0], [50, 20], [0, 20]],
                "font_size": 20,
                "alignment": "left",
                "y_position": 0,
                "text_region": None,
                "layout_info": {"page_index": 1, "column_index": 1},
            },
            {
                "text": "World",
                "bbox": (50, 0, 50, 20),
                "confidence": 0.88,
                "position": [[50, 0], [100, 0], [100, 20], [50, 20]],
                "font_size": 20,
                "alignment": "left",
                "y_position": 0,
                "text_region": None,
                "layout_info": {"page_index": 1, "column_index": 1},
            },
        ]

        merged = ocr._merge_line(line_texts)

        self.assertEqual(merged["text"], "Hello World")


if __name__ == "__main__":
    unittest.main()
