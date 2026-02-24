"""Markdown generator for Obsidian"""

from datetime import datetime
from typing import List, Dict, Tuple, Optional
import os
import re
import config


class ObsidianMarkdownGenerator:
    """Generate Obsidian-compatible markdown from OCR results"""

    def __init__(self, frontmatter=True, enable_callouts=True):
        self.frontmatter = frontmatter
        self.enable_callouts = enable_callouts

    def generate(self, images_data, output_path, source_dir):
        with open(output_path, "w", encoding="utf-8") as f:
            if self.frontmatter:
                f.write(self._create_frontmatter(source_dir))

            title = self._extract_title(images_data)
            f.write(f"# {title}\n\n")

            if config.IMPROVE_READABILITY:
                heading_level = (
                    config.CHAPTER_HEADING_LEVELS[0]
                    if config.CHAPTER_HEADING_LEVELS
                    else 2
                )
                f.write(f"#{'#' * (heading_level - 1)} Document Information\n\n")
                f.write(f"**Source:** `{source_dir}`\n")
                f.write(
                    f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                f.write(f"**Type:** {getattr(config, 'DOCUMENT_TYPE', 'booklet')}\n\n")
            else:
                f.write(f"**Source:** `{source_dir}`\n")
                f.write(
                    f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )

            f.write("---\n\n")

            for i, image_data in enumerate(images_data, 1):
                if image_data.get("error"):
                    f.write(f"\n### Page {i}\n\n")
                    f.write(f"> [!error]\n")
                    f.write(f"> Error processing image: {image_data['error']}\n\n")
                    continue

                content = self._format_page_content_with_layout(image_data["results"])
                if content.strip():
                    f.write(content)
                    if self.enable_callouts and config.EMBED_SOURCE_IMAGES:
                        relative_path = os.path.relpath(
                            image_data["image_path"], os.path.dirname(output_path)
                        )
                        callout_type = self._detect_page_callout_type(image_data)
                        f.write(
                            f"\n> [!{callout_type}]- Page {i}{' #' + '_'.join(config.DEFAULT_TAGS) if config.DEFAULT_TAGS else ''}\n"
                        )
                        f.write(f"> ![[{relative_path}]]\n\n")

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

            if len(text) < 3 or not text.replace(" ", "").isalnum():
                continue

            if font_size > max_font_size:
                max_font_size = font_size
                title_candidate = text

        return title_candidate if title_candidate else "CD Booklet OCR"

    def _create_frontmatter(self, source_dir) -> str:
        import hashlib

        source_bytes = source_dir.encode()
        content_hash = hashlib.md5(source_bytes).hexdigest()[:8]

        tags = getattr(config, "DEFAULT_TAGS", ["ocr", "booklet", "cd-doc"])
        doc_type = getattr(config, "DOCUMENT_TYPE", "booklet")

        frontmatter = "---\n"
        frontmatter += f"created: {datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        frontmatter += f"modified: {datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        frontmatter += f"id: booklet_{content_hash}\n"
        frontmatter += f"type: {doc_type}\n"
        frontmatter += f"source: {source_dir}\n"
        frontmatter += "tags:\n"
        for tag in tags:
            frontmatter += f"  - {tag}\n"
        if config.DETECT_CHAPTERS:
            for level in config.CHAPTER_HEADING_LEVELS:
                frontmatter += f"  - h{level}\n"
        frontmatter += "---\n\n"

        return frontmatter

    def _format_page_content(self, ocr_results: List[Dict]) -> str:
        if not ocr_results:
            return ""

        lines = self._group_into_lines(ocr_results)
        paragraphs = self._group_into_paragraphs(lines)
        markdown_lines = []

        for paragraph in paragraphs:
            formatted = self._format_paragraph(paragraph)
            if formatted:
                markdown_lines.append(formatted)
                markdown_lines.append("")

        return "\n".join(markdown_lines)

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
        current_col = None

        for page_idx, col_idx in sorted_keys:
            results = grouped[(page_idx, col_idx)]

            if page_idx != current_page:
                if current_page is not None:
                    markdown_parts.append("\n---\n")
                current_page = page_idx
                current_col = None

            if col_idx != current_col:
                if current_col is not None:
                    markdown_parts.append("\n---\n")
                current_col = col_idx

            # Results are already grouped by ocr_processor.group_text_lines
            # Each result is a line, so we just need to format them
            for text_info in results:
                formatted = self._format_single_line(text_info)
                if formatted:
                    markdown_parts.append(formatted)
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

        # Apply heading
        if styles.get("is_heading") and styles.get("heading_level"):
            result = f"{'#' * styles['heading_level']} {result}"
        elif styles.get("is_list"):
            list_type = styles.get("list_type", "bullet")
            if list_type == "numbered":
                result = f"1. {result}"
            elif list_type == "lettered":
                result = f"a. {result}"
            else:
                result = f"- {result}"

        # Apply bold/italic (not on headings)
        if not styles.get("is_heading"):
            if styles.get("is_bold") and styles.get("is_italic"):
                result = f"***{result}***"
            elif styles.get("is_bold"):
                result = f"**{result}**"
            elif styles.get("is_italic"):
                result = f"*{result}*"

        # Apply centering
        if styles.get("is_centered") and not styles.get("is_heading"):
            result = f"<center>{result}</center>"

        return result

    def _group_into_lines(
        self, ocr_results: List[Dict], y_threshold: float = 10
    ) -> List[List[Dict]]:
        """Group OCR results into lines based on y position"""
        if not ocr_results:
            return []

        lines = []
        current_line = []
        last_y = None

        for text_info in ocr_results:
            y_pos = text_info.get("y_position", 0)

            if last_y is None:
                current_line = [text_info]
            elif abs(y_pos - last_y) <= y_threshold:
                current_line.append(text_info)
            else:
                if current_line:
                    lines.append(current_line)
                current_line = [text_info]

            last_y = y_pos

        if current_line:
            lines.append(current_line)

        for line in lines:
            line.sort(key=lambda x: x.get("bbox", (0, 0, 0, 0))[0])

        return lines

    def _group_into_paragraphs(
        self, lines: List[List[Dict]], gap_threshold: float = 30
    ) -> List[List[List[Dict]]]:
        """Group lines into paragraphs based on vertical gaps"""
        if not lines:
            return []

        paragraphs = []
        current_paragraph = []
        last_y = None

        for line in lines:
            y_pos = max(t.get("y_position", 0) + t.get("font_size", 0) for t in line)

            if last_y is None:
                current_paragraph = [line]
            elif (y_pos - last_y) <= gap_threshold:
                current_paragraph.append(line)
            else:
                if current_paragraph:
                    paragraphs.append(current_paragraph)
                current_paragraph = [line]

            last_y = y_pos

        if current_paragraph:
            paragraphs.append(current_paragraph)

        return paragraphs

    def _format_paragraph(self, paragraph: List[List[Dict]]) -> str:
        """Format a paragraph into markdown"""
        if not paragraph:
            return ""

        all_text = []
        has_heading = False
        heading_level = None
        is_centered = False
        is_list = False
        list_type = None
        is_bold = False
        is_italic = False

        for line in paragraph:
            line_text = []
            for text_info in line:
                text = text_info.get("text", "")
                styles = text_info.get("styles", {})

                if not all_text:
                    has_heading = styles.get("is_heading", False)
                    heading_level = styles.get("heading_level")
                    is_centered = styles.get("is_centered", False)
                    is_list = styles.get("is_list", False)
                    list_type = styles.get("list_type")
                    is_bold = styles.get("is_bold", False)
                    is_italic = styles.get("is_italic", False)

                line_text.append(text)

            all_text.append(" ".join(line_text))

        combined = " ".join(all_text)
        combined = self._clean_text(combined)

        if not combined:
            return ""

        result = combined

        if has_heading and heading_level:
            result = f"{'#' * heading_level} {result}"
        elif is_list:
            if list_type == "numbered":
                result = f"1. {result}"
            elif list_type == "lettered":
                result = f"a. {result}"
            else:
                result = f"- {result}"

        if not has_heading:
            if is_bold and is_italic:
                result = f"***{result}***"
            elif is_bold:
                result = f"**{result}**"
            elif is_italic:
                result = f"*{result}*"

        if is_centered and not has_heading:
            result = f"<center>{result}</center>"

        return result

    def _clean_text(self, text: str) -> str:
        if not getattr(config, "CLEAN_OCR_ARTIFACTS", True):
            return text.strip()

        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[|\\]{2,}", "", text)
        text = re.sub(r"[\u2010-\u2015]{2,}", "-", text)
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)
        text = re.sub(r"([.,!?;:])([^\s.,!?;:])", r"\1 \2", text)
        text = re.sub(r"s[©®TM+]s", " ", text)

        text = re.sub(r"\+#\s*$", "", text)
        text = re.sub(r"\+\*\s*$", "", text)
        return text.strip()

    def _detect_page_callout_type(self, image_data: Dict) -> str:
        results = image_data.get("results", [])

        if not results:
            return "info"

        heading_count = 0
        list_count = 0
        text_count = 0

        for text_info in results:
            styles = text_info.get("styles", {})

            if styles.get("is_heading"):
                heading_count += 1
            elif styles.get("is_list"):
                list_count += 1
            else:
                text_count += 1

        if heading_count >= 3:
            return "note"
        elif list_count > text_count:
            return "tip"
        elif text_count == 0:
            return "blank"
        else:
            return "info"


def format_text_block(text_info, min_heading_size=24):
    """
    Format individual text block with markdown

    Args:
        text_info: Text information dictionary
        min_heading_size: Minimum font size for heading

    Returns:
        Formatted markdown string
    """
    text = text_info["text"]
    font_size = text_info["font_size"]
    styles = text_info.get("styles", {})

    # Apply heading formatting
    if styles.get("is_heading") and styles.get("heading_level"):
        level = styles["heading_level"]
        heading_markers = "#" * level
        text = f"{heading_markers} {text}"

    # Apply list formatting
    if styles.get("is_list"):
        list_type = styles.get("list_type", "bullet")
        if list_type == "bullet":
            text = f"- {text}"
        elif list_type == "numbered":
            text = f"1. {text}"
        elif list_type == "lettered":
            text = f"a. {text}"

    # Apply centering
    if styles.get("is_centered") and not styles.get("is_heading"):
        text = f"<center>{text}</center>"

    return text

    """Clean specific OCR artifacts like +# +* etc"""
    text = re.sub(r'\+#\s*$', '', text)
    text = re.sub(r'\+\*\s*$', '', text)
    text = re.sub(r'^\+#\s*', '', text)
    text = re.sub(r'^\+\*\s*', '', text)
    return text.strip()

    return result

