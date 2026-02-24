"""Unit tests for config module"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import config


class TestConfig(unittest.TestCase):
    """Test configuration values"""

    def test_logging_config(self):
        """Test logging configuration defaults"""
        self.assertIsNotNone(config.LOG_LEVEL)
        self.assertIn(
            config.LOG_LEVEL, ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )
        self.assertIsInstance(config.LOG_FILE, (str, type(None)))
        self.assertIsInstance(config.LOG_TO_CONSOLE, bool)

    def test_ocr_config(self):
        """Test OCR configuration"""
        self.assertIn(config.OCR_LANGUAGE, ["ch", "en", "chinese", "english"])
        self.assertIsInstance(config.OCR_USE_GPU, bool)
        self.assertIsNotNone(config.TESSERACT_CONFIG)

    def test_style_detection_thresholds(self):
        """Test style detection thresholds"""
        self.assertGreater(config.MIN_HEADING_FONT_SIZE, 0)
        self.assertGreater(config.BOLD_STROKE_RATIO, 0)
        self.assertLess(config.BOLD_STROKE_RATIO, 1)
        self.assertGreater(config.ITALIC_MIN_ANGLE, 0)
        self.assertLess(config.ITALIC_MAX_ANGLE, 90)

    def test_heading_levels(self):
        """Test heading level configuration"""
        self.assertIsInstance(config.HEADING_SIZE_LEVELS, dict)
        self.assertGreater(len(config.HEADING_SIZE_LEVELS), 0)
        for level, size in config.HEADING_SIZE_LEVELS.items():
            self.assertIn(level, [1, 2, 3, 4, 5, 6])
            self.assertGreater(size, 0)

    def test_layout_analysis_config(self):
        """Test layout analysis configuration"""
        self.assertIsInstance(config.ENABLE_LAYOUT_ANALYSIS, bool)
        self.assertIn(config.LAYOUT_ANALYSIS_METHOD, ["contour", "projection"])
        self.assertGreater(config.MIN_TEXT_AREA, 0)
        self.assertGreater(config.PAGE_SPLIT_THRESHOLD, 0)

    def test_output_settings(self):
        """Test output settings"""
        self.assertIsInstance(config.OBSIDIAN_FRONTMATTER, bool)
        self.assertIsInstance(config.ENABLE_CALLOUTS, bool)
        self.assertIsInstance(config.EMBED_SOURCE_IMAGES, bool)
        self.assertIsInstance(config.PRESERVE_LINE_BREAKS, bool)
        self.assertIsInstance(config.CLEAN_OCR_ARTIFACTS, bool)

    def test_tags_and_document_type(self):
        """Test tags and document type"""
        self.assertIsInstance(config.DEFAULT_TAGS, list)
        self.assertGreater(len(config.DEFAULT_TAGS), 0)
        self.assertIn(
            config.DOCUMENT_TYPE, ["booklet", "brochure", "manual", "flyer", "leaflet"]
        )

    def test_tesseract_path(self):
        """Test Tesseract path configuration"""
        self.assertIsNotNone(config.TESSERACT_PATH)
        self.assertIsInstance(config.TESSERACT_PATH, str)

    def test_y_group_threshold(self):
        """Test Y grouping threshold"""
        self.assertGreater(config.Y_GROUP_THRESHOLD, 0)

    def test_paragraph_gap_threshold(self):
        """Test paragraph gap threshold"""
        self.assertGreater(config.PARAGRAPH_GAP_THRESHOLD, 0)


if __name__ == "__main__":
    unittest.main()
