"""RapidOCR-based processor with improved multi-column layout handling"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import re
import config
from logger import get_logger

logger = get_logger(__name__)


class RapidBookletOCR:
    """OCR processor using RapidOCR with improved layout handling"""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self.reader = None
        self._initialize()

    def _initialize(self):
        try:
            from rapidocr_onnxruntime import RapidOCR as _RapidOCR

            self.reader = _RapidOCR()
            logger.info("RapidOCR initialized successfully")
        except ImportError:
            logger.error(
                "RapidOCR not installed. Run: pip install rapidocr-onnxruntime"
            )
            raise

    def process_image(self, image) -> List[Dict]:
        if hasattr(image, "mode"):
            image_np = np.array(image.convert("RGB"))
        else:
            image_np = image

        page_regions = self._detect_page_regions(image_np)
        all_texts = []

        for page_idx, page_region in enumerate(page_regions, 1):
            columns = self._detect_columns_in_region(image_np, page_region)

            for col_idx, col_region in enumerate(columns, 1):
                texts = self._process_region(image_np, col_region, page_idx, col_idx)
                all_texts.extend(texts)

        all_texts.sort(
            key=lambda x: (
                x.get("layout_info", {}).get("page_index", 1),
                x.get("layout_info", {}).get("column_index", 1),
                x["y_position"],
                x["bbox"][0],
            )
        )

        return all_texts

    def _detect_page_regions(self, image: np.ndarray) -> List[Tuple]:
        height, width = image.shape[:2]

        gray = (
            cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        )
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        horizontal_proj = np.sum(binary, axis=0)

        strip_width = width // 8
        center_x = width // 2
        left_bound = center_x - strip_width // 2
        right_bound = center_x + strip_width // 2

        center_proj = horizontal_proj[left_bound:right_bound]
        avg_proj = np.mean(horizontal_proj)
        min_center = np.min(center_proj)
        threshold = avg_proj * 0.3

        if min_center < threshold:
            gap_idx = left_bound + np.argmin(center_proj)
            return [(0, 0, gap_idx, height), (gap_idx, 0, width - gap_idx, height)]

        return [(0, 0, width, height)]

    def _detect_columns_in_region(
        self, image: np.ndarray, region: Tuple
    ) -> List[Tuple]:
        x, y, w, h = region
        if w <= 0 or h <= 0:
            return [region]

        # Too narrow for multiple columns - likely title page
        if w < 900:
            return [region]

        
        # Temporarily disable column detection to avoid title splitting
        # TODO: Implement smarter column detection that respects page sections
        return [region]
        region_img = image[y : y + h, x : x + w]
        gray = (
            cv2.cvtColor(region_img, cv2.COLOR_RGB2GRAY)
            if len(region_img.shape) == 3
            else region_img
        )
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        vertical_proj = np.sum(binary, axis=1)
        if np.max(vertical_proj) == 0:
            return [region]

        vertical_proj = vertical_proj / np.max(vertical_proj)

        has_text_rows = np.sum(vertical_proj > 0.1)
        if has_text_rows < h * 0.3:
            return [region]

        horizontal_proj = np.sum(binary, axis=0)
        if np.max(horizontal_proj) == 0:
            return [region]

        horizontal_proj = horizontal_proj / np.max(horizontal_proj)
        # Find widest low-projection region in middle 50%
        start_pct = 0.25
        end_pct = 0.75
        start_x = int(w * start_pct)
        end_x = int(w * end_pct)

        middle_proj = horizontal_proj[start_x:end_x]
        threshold = 0.15
        low_indices = np.where(middle_proj < threshold)[0]

        if len(low_indices) == 0:
            return [region]

        low_indices_abs = low_indices + start_x
        regions = []
        in_region = False
        region_start = low_indices_abs[0]
        last_idx = low_indices_abs[0]

        for idx in low_indices_abs[1:]:
            if idx - last_idx <= 10:
                in_region = True
                last_idx = idx
            else:
                if in_region:
                    regions.append((region_start, last_idx))
                regions.append((last_idx, last_idx))
                region_start = idx
                last_idx = idx
                in_region = False

        if in_region:
            regions.append((region_start, last_idx))

        # Merge nearby regions
        merged_regions = []
        merge_threshold = 30
        if regions:
            merged_regions = [list(regions[0])]
            for rs, re in regions[1:]:
                last = merged_regions[-1]
                if rs - last[1] <= merge_threshold:
                    merged_regions[-1][1] = re
                else:
                    merged_regions.append([rs, re])

        # Find widest region
        if not merged_regions:
            return [region]

        widest = max(merged_regions, key=lambda r: r[1] - r[0])
        widest_width = widest[1] - widest[0]

        # Must be at least 3% of width
        if widest_width < w * 0.03:
            return [region]

        gap_center = (widest[0] + widest[1]) // 2
        # Check if text would span across the gap - if so, don't split
        if self._would_split_wide_text(region_img, gap_center, w):
            return [region]
        col1 = (x, y, gap_center, h)
        col2 = (x + gap_center, y, w - gap_center, h)
        return [col1, col2]

    def _would_split_wide_text(self, region_img, gap_center, w):
        if not self.reader:
            return False
        left_half = region_img[:, :gap_center]
        right_half = region_img[:, gap_center:]

        try:
            left_result = self.reader(left_half)
            right_result = self.reader(right_half)
        except:
            return False

        left_width_check = gap_center * 0.55
        wide_texts = 0
        total_left = 0
        if left_result and left_result[0]:
            total_left = len(left_result[0])
            for pts, txt, conf in left_result[0]:
                x_coords = [p[0] for p in pts]
                if max(x_coords) - min(x_coords) > left_width_check:
                    wide_texts += 1

        total_right = 0
        if right_result and right_result[0]:
            total_right = len(right_result[0])

        total = total_left + total_right
        if total == 0:
            return False

        if wide_texts / total > 0.15:
            return True

        if total < 10:
            return True

        return False


    def _process_region(
        self, image: np.ndarray, region: Tuple, page_index: int, column_index: int
    ) -> List[Dict]:
        x, y, w, h = region
        if w <= 0 or h <= 0:
            return []

        region_img = image[y : y + h, x : x + w]

        try:
            result = self.reader(region_img)
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return []

        texts = []
        if result and result[0]:
            for item in result[0]:
                points, text, confidence = item

                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]

                abs_x_min = int(min(x_coords)) + x
                abs_y_min = int(min(y_coords)) + y
                abs_x_max = int(max(x_coords)) + x
                abs_y_max = int(max(y_coords)) + y

                width_text = abs_x_max - abs_x_min
                height_text = abs_y_max - abs_y_min

                if float(confidence) < 0.3 or width_text < 5 or height_text < 5:
                    continue

                image_center_x = image.shape[1] // 2
                text_center_x = abs_x_min + width_text // 2

                if abs(text_center_x - image_center_x) < width_text * 0.3:
                    alignment = "center"
                elif text_center_x < image_center_x:
                    alignment = "left"
                else:
                    alignment = "right"

                font_size = int(height_text * 0.8)

                texts.append(
                    {
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": (abs_x_min, abs_y_min, width_text, height_text),
                        "font_size": font_size,
                        "text_width": width_text,
                        "alignment": alignment,
                        "y_position": abs_y_min,
                        "text_region": None,
                        "layout_info": {
                            "page_index": page_index,
                            "column_index": column_index,
                        },
                        "position": [[p[0] + x, p[1] + y] for p in points],
                    }
                )

        return texts

    def group_text_lines(
        self, texts: List[Dict], y_threshold: float = 15
    ) -> List[Dict]:
        if not texts:
            return []

        layout_groups = {}
        for text in texts:
            layout_info = text.get("layout_info", {})
            page_idx = layout_info.get("page_index", 1)
            col_idx = layout_info.get("column_index", 1)
            key = (page_idx, col_idx)
            if key not in layout_groups:
                layout_groups[key] = []
            layout_groups[key].append(text)

        all_grouped = []
        for key in sorted(layout_groups.keys()):
            group_texts = layout_groups[key]
            group_texts.sort(key=lambda x: (x["y_position"], x["bbox"][0]))
            grouped = self._group_single_layout(group_texts, y_threshold)
            all_grouped.extend(grouped)

        return all_grouped

    def _group_single_layout(self, texts: List[Dict], y_threshold: float) -> List[Dict]:
        if not texts:
            return []

        grouped_lines = []
        current_line = [texts[0]]
        current_y = texts[0]["y_position"]

        for text in texts[1:]:
            y_diff = abs(text["y_position"] - current_y)

            if y_diff <= y_threshold:
                current_line.append(text)
            else:
                current_line.sort(key=lambda x: x["bbox"][0])
                merged = self._merge_line(current_line)
                grouped_lines.append(merged)

                current_line = [text]
                current_y = text["y_position"]

        if current_line:
            current_line.sort(key=lambda x: x["bbox"][0])
            merged = self._merge_line(current_line)
            grouped_lines.append(merged)

        return grouped_lines

    def _merge_line(self, line_texts: List[Dict]) -> Dict:
        if len(line_texts) == 1:
            return line_texts[0]

        line_texts = sorted(line_texts, key=lambda x: x["bbox"][0])

        avg_font_size = sum(t.get("font_size", 20) for t in line_texts) / len(
            line_texts
        )
        horizontal_gap_threshold = avg_font_size * 1.5

        text_parts = []
        prev_x_end = None

        for text_info in line_texts:
            text = text_info["text"].strip()
            tx, ty, tw, th = text_info["bbox"]
            x_end = tx + tw

            if prev_x_end is not None:
                gap = tx - prev_x_end
                if gap <= horizontal_gap_threshold:
                    text_parts.append(" ")
                else:
                    text_parts.append("  ")

            text_parts.append(text)
            prev_x_end = x_end

        combined_text = "".join(text_parts).strip()

        x_min = min(t["bbox"][0] for t in line_texts)
        y_min = min(t["bbox"][1] for t in line_texts)
        x_max = max(t["bbox"][0] + t["bbox"][2] for t in line_texts)
        y_max = max(t["bbox"][1] + t["bbox"][3] for t in line_texts)

        width = x_max - x_min
        height = y_max - y_min

        avg_confidence = sum(t["confidence"] for t in line_texts) / len(line_texts)
        first_text = line_texts[0]

        return {
            "text": combined_text,
            "confidence": avg_confidence,
            "position": line_texts[0]["position"],
            "bbox": (x_min, y_min, width, height),
            "font_size": first_text["font_size"],
            "text_width": width,
            "alignment": first_text["alignment"],
            "y_position": y_min,
            "text_region": None,
            "layout_info": first_text.get(
                "layout_info", {"page_index": 1, "column_index": 1}
            ),
        }

    def classify_text_style(
        self, text_info: Dict, min_heading_size: int = None
    ) -> Dict:
        font_size = text_info["font_size"]
        alignment = text_info["alignment"]
        text = text_info["text"]

        if min_heading_size is None:
            min_heading_size = getattr(config, "MIN_HEADING_FONT_SIZE", 36)

        heading_levels = getattr(
            config, "HEADING_SIZE_LEVELS", {1: 48, 2: 42, 3: 38, 4: 36}
        )

        styles = {
            "is_heading": False,
            "heading_level": None,
            "is_bold": False,
            "is_italic": False,
            "is_centered": False,
            "is_list": False,
            "list_type": None,
            "markdown_prefix": "",
            "markdown_suffix": "",
        }

        if font_size >= min_heading_size:
            styles["is_heading"] = True
            styles["is_centered"] = alignment == "center"

            for level, threshold in sorted(heading_levels.items(), reverse=True):
                if font_size >= threshold:
                    styles["heading_level"] = level
                    break

            if not styles["heading_level"]:
                styles["heading_level"] = 4

        if alignment == "center" and not styles["is_heading"]:
            styles["is_centered"] = True

        track_pattern = r"^(\d+)\s+(.*?)\s*[\[\{][\d:]+[\]\}]"
        if re.match(track_pattern, text):
            styles["is_list"] = True
            styles["list_type"] = "numbered"
        elif re.match(r"^\d+[\.\)]\s+", text):
            styles["is_list"] = True
            styles["list_type"] = "numbered"
        elif re.match(r"^[\*\•\-\→]\s+", text):
            styles["is_list"] = True
            styles["list_type"] = "bullet"

        if styles["is_heading"] and styles["heading_level"]:
            styles["markdown_prefix"] = "#" * styles["heading_level"] + " "

        if styles["is_centered"] and not styles["is_heading"]:
            styles["markdown_prefix"] = "<center>" + styles["markdown_prefix"]
            styles["markdown_suffix"] = "</center>"

        return styles
