"""Markdown generator for clean output matching reference format"""

from datetime import datetime
from typing import List, Dict, Tuple, Optional
import os
import re
import config


class ObsidianMarkdownGenerator:
    """Generate clean markdown from OCR results"""

    def __init__(self, frontmatter=True, enable_callouts=True):
        self.frontmatter = frontmatter
        self.enable_callouts = enable_callouts

    def generate(self, images_data, output_path, source_dir):
        with open(output_path, "w", encoding="utf-8") as f:

            for i, image_data in enumerate(images_data, 1):
                if image_data.get("error"):
                    f.write(f"\n### Page {i}\n\n")
                    f.write(f"Error: {image_data['error']}\n\n")
                    continue

                content = self._format_page_content_with_layout(image_data["results"])
                if content.strip():
                    f.write(content)

    def _format_page_content_with_layout(self, ocr_results: List[Dict]) -> str:
        if not ocr_results:
            return ""


        grouped = {}
        for result in ocr_results:
            layout_info = result.get("layout_info", {})
            page_idx = layout_info.get("page_index", 1)
            col_idx = layout_info.get("column_index", 1)
            key = (page_idx, col_idx)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(result)

        sorted_keys = sorted(grouped.keys())
        markdown_parts = []
        current_page = None

        for page_idx, col_idx in sorted_keys:
            results = grouped[(page_idx, col_idx)]


            if page_idx != current_page:
                if current_page is not None:
                    markdown_parts.append("\n---\n")
                current_page = page_idx


            # Group lines into paragraphs based on y-position gaps
            paragraphs = self._group_into_paragraphs(results)
            
            for paragraph in paragraphs:
                if not paragraph:
                    continue
                # Merge paragraph lines - handle hyphens at line ends
                texts = [p.get("text", "") for p in paragraph]
                merged_text = ""
                for i in range(len(texts)):
                    if i > 0:
                        if texts[i-1].rstrip().endswith("-"):
                            merged_text += texts[i]  # No space after hyphen
                        else:
                            merged_text += " " + texts[i]  # Normal space
                    else:
                        merged_text = texts[i]

                merged_text = self._clean_text(merged_text)
                if merged_text:
                    # Check if first line is a heading and apply formatting
                    first_line = paragraph[0]
                    formatted_text = self._apply_formatting(first_line, merged_text)
                    markdown_parts.append(formatted_text)
                    markdown_parts.append("")

        return "\n".join(markdown_parts)

    def _format_single_line(self, text_info: Dict) -> str:
        text = text_info.get("text", "")
        styles = text_info.get("styles", {})

        if not text or not text.strip():
            return ""

        text = self._clean_text(text)
        if not text:
            return ""

        result = text


        if styles.get("is_heading") and styles.get("heading_level"):
            result = f"{'#' * styles['heading_level']} {result}"

        return result

    def _group_into_paragraphs(self, lines: List[Dict]) -> List[List[Dict]]:
        """Group lines into paragraphs based on y-position gaps"""
        if not lines:
            return []

        paragraphs = []
        current_paragraph = [lines[0]]
        last_y = lines[0].get("y_position", 0)
        last_font_size = lines[0].get("font_size", 12)

        for line in lines[1:]:
            y_pos = line.get("y_position", 0)
            font_size = line.get("font_size", 12)
            y_diff = y_pos - last_y
            expected_gap = last_font_size * 1.5

            # If gap is small relative to line height, same paragraph
            y_diff_normalized = y_diff / (last_font_size if last_font_size > 0 else 12)
            if y_diff_normalized < 2.5:
                current_paragraph.append(line)
            else:
                if current_paragraph:
                    paragraphs.append(current_paragraph)
                current_paragraph = [line]
            last_y = y_pos
            last_font_size = font_size

        if current_paragraph:
            paragraphs.append(current_paragraph)

        return paragraphs

    def _apply_formatting(self, reference_line: Dict, text: str) -> str:
        """Apply formatting from reference line to merged text"""
        styles = reference_line.get("styles", {})
        result = text

        if styles.get("is_heading") and styles.get("heading_level"):
            result = f"{'#' * styles['heading_level']} {result}"

        return result

    def _clean_text(self, text: str) -> str:
        """Clean OCR artifacts"""
        if not text:
            return ""


        text = re.sub(r"\s+", " ", text)

        # Fix bracket/brace confusion: OCR often mixes () [] {}
        # Convert to consistent format for time stamps: {3:10}
        text = re.sub(r"[\(\[\{](\d+):\s*(\d+)[\)\]\}]", r"{\1:\2}", text)

        # Hyphen repair: remove hyphens at line breaks
        text = re.sub(r"(\w+)-\s+", r"\1 ", text)
        text = re.sub(r"-\s*$", "", text)
        # Also remove hyphens between letters (word-break hyphens)
        text = re.sub(r"([a-zA-Z]+)-([a-zA-Z]+)", r"\1 \2", text)


        # Fix words joined without spaces after paragraph merging
        text = re.sub(r"([a-z])([A-Z][a-z])", r"\1 \2", text)



        text = re.sub(r"\+#\s*$", "", text)
        text = re.sub(r"\+\*\s*$", "", text)
        text = re.sub(r"\+\w\s*$", "", text)

        return text.strip()

    def _extract_title(self, images_data: List[Dict]) -> str:
        """Extract title from first page OCR results"""
        if not images_data or images_data[0].get("error"):
            return "CD Booklet OCR"

        results = images_data[0].get("results", [])
        if not results:
            return "CD Booklet OCR"

        title_candidate = None
        max_font_size = 0

        for text_info in results[:10]:
            font_size = text_info.get("font_size", 0)
            text = text_info.get("text", "").strip()

            if len(text) < 3:
                continue

            if font_size > max_font_size:
                max_font_size = font_size
                title_candidate = text

        return title_candidate if title_candidate else "CD Booklet OCR"

    def _create_frontmatter(self, source_dir) -> str:
        return ""

    def _format_page_content(self, ocr_results: List[Dict]) -> str:
        return self._format_page_content_with_layout(ocr_results)

    def _detect_page_callout_type(self, image_data: Dict) -> str:
        return "info"


def format_text_block(text_info, min_heading_size=24):
    """Format individual text block with markdown"""
    text = text_info["text"]
    styles = text_info.get("styles", {})

    if styles.get("is_heading") and styles.get("heading_level"):
        level = styles["heading_level"]
        heading_markers = "#" * level
        text = f"{heading_markers} {text}"

    return text
