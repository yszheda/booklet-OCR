"""Unit tests for layout_analyzer module"""

import unittest
import sys
import cv2
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from layout_analyzer import LayoutAnalyzer


class TestLayoutAnalyzer(unittest.TestCase):
    """Test layout analyzer functionality"""

    def setUp(self):
        """Setup layout analyzer"""
        self.analyzer = LayoutAnalyzer()

    def create_test_image(self, width=800, height=1000, pages=1, columns=1):
        """Create a test image with specified layout"""
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        if pages > 1:
            gap_y = int(height // (pages + 1))
            for i in range(1, pages):
                y_pos = i * gap_y
                cv2.rectangle(
                    img, (0, y_pos - 10), (width, y_pos + 10), (255, 255, 255), -1
                )

        if columns > 1:
            gap_x = int(width // (columns + 1))
            for i in range(1, columns):
                x_pos = i * gap_x
                cv2.rectangle(
                    img, (x_pos - 10, 0), (x_pos + 10, height), (255, 255, 255), -1
                )

        return img

    def test_layout_analyzer_init(self):
        """Test layout analyzer initialization"""
        self.assertIsNotNone(self.analyzer)

    def test_detect_pages_single(self):
        """Test single page detection"""
        image = self.create_test_image(pages=1)

        pages = self.analyzer.detect_pages(image)

        self.assertGreater(len(pages), 0)

    def test_detect_pages_multiple(self):
        """Test multi-page detection"""
        image = self.create_test_image(pages=2)

        pages = self.analyzer.detect_pages(image)

        self.assertGreater(len(pages), 0)

    def test_detect_columns_single(self):
        """Test single column detection"""
        image = self.create_test_image(columns=1)

        columns = self.analyzer.detect_columns(image)

        self.assertGreater(len(columns), 0)

    def test_detect_columns_double(self):
        """Test double column detection"""
        image = self.create_test_image(columns=2)

        columns = self.analyzer.detect_columns(image)

        self.assertGreater(len(columns), 0)

    def test_detect_columns_triple(self):
        """Test triple column detection"""
        image = self.create_test_image(columns=3)

        columns = self.analyzer.detect_columns(image, max_columns=3)

        self.assertGreater(len(columns), 0)

    def test_detect_image_regions(self):
        """Test image region detection"""
        image = np.ones((600, 800, 3), dtype=np.uint8) * 255

        cv2.rectangle(image, (100, 100, 300, 200), (128, 128, 128), -1)

        regions = self.analyzer.detect_image_regions(image)

        self.assertIsInstance(regions, list)

    def test_is_text_block_no_overlap(self):
        """Test text block with no overlap with image region"""
        text_bbox = (50, 50, 100, 20)
        image_regions = [
            {"bbox": (200, 200, 100, 100)},
        ]

        is_text = self.analyzer.is_text_block(text_bbox, image_regions)

        self.assertTrue(is_text)

    def test_is_text_block_with_overlap(self):
        """Test text block with overlap"""
        text_bbox = (50, 50, 100, 100)
        image_regions = [
            {"bbox": (100, 100, 100, 100)},
        ]

        result = self.analyzer.is_text_block(text_bbox, image_regions)

        self.assertIsInstance(result, bool)

    def test_filter_image_regions_empty(self):
        """Test filtering with no text blocks"""
        image = np.ones((600, 800, 3), dtype=np.uint8) * 255
        text_blocks = []

        filtered = self.analyzer.filter_image_regions(image, text_blocks)

        self.assertEqual(len(filtered), 0)

    def test_analyze_layout_single_page(self):
        """Test analyzing layout of single page"""
        image = self.create_test_image(pages=1, columns=1)

        layout = self.analyzer.analyze_layout(image)

        self.assertIsInstance(layout, list)
        self.assertGreater(len(layout), 0)

    def test_analyze_layout_multi_column(self):
        """Test analyzing layout with multiple columns"""
        image = self.create_test_image(pages=1, columns=2)

        layout = self.analyzer.analyze_layout(image)

        self.assertIsInstance(layout, list)
        self.assertGreater(len(layout), 0)

    def test_extract_by_contours(self):
        """Test text extraction using contours"""
        image = np.ones((600, 800), dtype=np.uint8) * 255

        cv2.putText(
            image, "Test", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2
        )

        regions = self.analyzer._extract_by_contours(image)

        self.assertIsInstance(regions, list)

    def test_extract_by_projection(self):
        """Test text extraction using projection"""
        image = np.ones((600, 800), dtype=np.uint8) * 255

        cv2.rectangle(image, (50, 50, 200, 30), (0, 0, 0), -1)

        regions = self.analyzer._extract_by_projection(image)

        self.assertIsInstance(regions, list)


if __name__ == "__main__":
    unittest.main()
