"""Unit tests for markdown_generator module"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from markdown_generator import ObsidianMarkdownGenerator, format_text_block

import config


class TestMarkdownGenerator(unittest.TestCase):
    """Test markdown generator functionality"""

    def setUp(self):
        """Setup test fixtures"""
        self.generator = ObsidianMarkdownGenerator(
            frontmatter=True, enable_callouts=True
        )
        self.output_dir = Path(__file__).parent / "test_output"
        self.output_dir.mkdir(exist_ok=True)

    def test_generator_init(self):
        """Test generator initialization"""
        gen = ObsidianMarkdownGenerator(frontmatter=True, enable_callouts=True)
        self.assertIsNotNone(gen)
        self.assertTrue(gen.frontmatter)
        self.assertTrue(gen.enable_callouts)

    def test_extract_title(self):
        """Test title extraction from OCR results"""
        images_data = [
            {
                "results": [
                    {"text": "Title", "font_size": 50},
                    {"text": "Subtitle", "font_size": 30},
                ]
            }
        ]

        title = self.generator._extract_title(images_data)

        self.assertEqual(title, "Title")

    def test_extract_title_no_results(self):
        """Test title extraction with no results"""
        images_data = []

        title = self.generator._extract_title(images_data)

        self.assertEqual(title, "CD Booklet OCR")

    def test_create_frontmatter(self):
        """Test frontmatter creation"""
        frontmatter = self.generator._create_frontmatter("./test_source")

        self.assertIn("---", frontmatter)
        self.assertIn("created:", frontmatter)
        self.assertIn("modified:", frontmatter)
        self.assertIn("source:", frontmatter)

    def test_format_page_content_empty(self):
        """Test formatting empty page content"""
        content = self.generator._format_page_content([])

        self.assertEqual(content, "")

    def test_format_page_content_with_layout(self):
        """Test formatting page content with layout info"""
        ocr_results = [
            {
                "text": "Heading",
                "styles": {"is_heading": True, "heading_level": 1, "is_bold": False},
                "y_position": 10,
            },
            {
                "text": "Normal text",
                "styles": {"is_heading": False, "is_bold": False},
                "y_position": 50,
            },
        ]

        content = self.generator._format_page_content_with_layout(ocr_results)

        self.assertIn("# Heading", content)

    def test_format_single_line_heading(self):
        """Test formatting single line as heading"""
        text_info = {
            "text": "Test Heading",
            "styles": {
                "is_heading": True,
                "heading_level": 2,
                "is_bold": False,
                "is_italic": False,
            },
        }

        formatted = self.generator._format_single_line(text_info)

        self.assertEqual(formatted, "## Test Heading")

    def test_format_single_line_bold(self):
        """Test formatting single line as bold"""
        text_info = {
            "text": "Bold Text",
            "styles": {
                "is_heading": False,
                "heading_level": None,
                "is_bold": True,
                "is_italic": False,
            },
        }

        formatted = self.generator._format_single_line(text_info)

        self.assertEqual(formatted, "**Bold Text**")

    def test_format_single_line_italic(self):
        """Test formatting single line as italic"""
        text_info = {
            "text": "Italic Text",
            "styles": {
                "is_heading": False,
                "heading_level": None,
                "is_bold": False,
                "is_italic": True,
            },
        }

        formatted = self.generator._format_single_line(text_info)

        self.assertEqual(formatted, "*Italic Text*")

    def test_format_single_line_bold_italic(self):
        """Test formatting single line as bold and italic"""
        text_info = {
            "text": "Bold Italic",
            "styles": {
                "is_heading": False,
                "heading_level": None,
                "is_bold": True,
                "is_italic": True,
            },
        }

        formatted = self.generator._format_single_line(text_info)

        self.assertEqual(formatted, "***Bold Italic***")

    def test_format_single_line_list_bullet(self):
        """Test formatting single line as bullet list"""
        text_info = {
            "text": "Item",
            "styles": {
                "is_heading": False,
                "heading_level": None,
                "is_list": True,
                "list_type": "bullet",
            },
        }

        formatted = self.generator._format_single_line(text_info)

        self.assertEqual(formatted, "- Item")

    def test_format_single_line_list_numbered(self):
        """Test formatting single line as numbered list"""
        text_info = {
            "text": "Item",
            "styles": {
                "is_heading": False,
                "heading_level": None,
                "is_list": True,
                "list_type": "numbered",
            },
        }

        formatted = self.generator._format_single_line(text_info)

        self.assertEqual(formatted, "1. Item")

    def test_format_single_line_centered(self):
        """Test formatting single line as centered"""
        text_info = {
            "text": "Centered",
            "styles": {
                "is_heading": False,
                "heading_level": None,
                "is_bold": False,
                "is_italic": False,
                "is_centered": True,
            },
        }

        formatted = self.generator._format_single_line(text_info)

        self.assertEqual(formatted, "<center>Centered</center>")

    def test_group_into_lines(self):
        """Test grouping OCR results into lines"""
        ocr_results = [
            {"y_position": 100, "bbox": (0, 100, 50, 20)},
            {"y_position": 100, "bbox": (50, 100, 50, 20)},
            {"y_position": 150, "bbox": (0, 150, 100, 20)},
        ]

        lines = self.generator._group_into_lines(ocr_results, y_threshold=15)

        self.assertEqual(len(lines), 2)

    def test_group_into_paragraphs(self):
        """Test grouping lines into paragraphs"""
        lines = [
            [{"y_position": 100, "font_size": 20}],
            [{"y_position": 130, "font_size": 20}],
            [{"y_position": 200, "font_size": 20}],
        ]

        paragraphs = self.generator._group_into_paragraphs(lines, gap_threshold=30)

        self.assertEqual(len(paragraphs), 2)

    def test_clean_text(self):
        """Test text cleaning"""
        text = "  Multiple   spaces  and  |||  "

        cleaned = self.generator._clean_text(text)

        self.assertNotIn("|||", cleaned)

    def test_detect_page_callout_type_info(self):
        """Test page callout type detection - info"""
        image_data = {
            "results": [
                {"styles": {"is_heading": False}},
                {"styles": {"is_heading": False}},
            ]
        }

        callout_type = self.generator._detect_page_callout_type(image_data)

        self.assertEqual(callout_type, "info")

    def test_detect_page_callout_type_note(self):
        """Test page callout type detection - note"""
        image_data = {
            "results": [
                {"styles": {"is_heading": True}},
                {"styles": {"is_heading": True}},
                {"styles": {"is_heading": True}},
                {"styles": {"is_heading": False}},
            ]
        }

        callout_type = self.generator._detect_page_callout_type(image_data)

        self.assertEqual(callout_type, "note")

    def test_detect_page_callout_type_tip(self):
        """Test page callout type detection - tip"""
        image_data = {
            "results": [
                {"styles": {"is_list": True}},
                {"styles": {"is_list": True}},
                {"styles": {"is_list": True}},
                {"styles": {"is_heading": False}},
            ]
        }

        callout_type = self.generator._detect_page_callout_type(image_data)

        self.assertEqual(callout_type, "tip")

    def test_generate_simple(self):
        """Test generating complete markdown file"""
        images_data = [
            {
                "image_path": str(self.output_dir / "test.jpg"),
                "results": [
                    {
                        "text": "Test Title",
                        "font_size": 50,
                        "styles": {
                            "is_heading": True,
                            "heading_level": 1,
                        },
                        "y_position": 10,
                    },
                ],
                "num_texts": 1,
            }
        ]

        output_path = self.output_dir / "test_generated.md"

        self.generator.generate(images_data, str(output_path), "./test")

        self.assertTrue(output_path.exists())


class TestFormatTextBlock(unittest.TestCase):
    """Test standalone format_text_block function"""

    def test_format_heading(self):
        """Test formatting heading"""
        text_info = {
            "text": "Title",
            "font_size": 40,
            "styles": {"is_heading": True, "heading_level": 2},
        }

        formatted = format_text_block(text_info, min_heading_size=30)

        self.assertEqual(formatted, "## Title")

    def test_format_list_bullet(self):
        """Test formatting bullet list"""
        text_info = {
            "text": "Item",
            "font_size": 20,
            "styles": {"is_heading": False, "is_list": True, "list_type": "bullet"},
        }

        formatted = format_text_block(text_info, min_heading_size=30)

        self.assertEqual(formatted, "- Item")


if __name__ == "__main__":
    unittest.main()
