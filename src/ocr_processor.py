"""OCR processing with style detection using Tesseract"""

import cv2
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import os
import re
import config
from logger import get_logger

logger = get_logger(__name__)

try:
    from layout_analyzer import LayoutAnalyzer

    LAYOUT_ANALYZER_AVAILABLE = True
except ImportError:
    LAYOUT_ANALYZER_AVAILABLE = False

try:
    import pytesseract

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA_PATH = Path(__file__).parent.parent / "tessdata"


class BookletOCR:
    """OCR processor for booklets with style detection using Tesseract"""

    def __init__(
        self, use_angle_cls: bool = True, lang: str = "ch", use_gpu: bool = False
    ):
        if not TESSERACT_AVAILABLE:
            raise ImportError(
                "pytesseract is required. Install with: pip install pytesseract"
            )

        lang_map = {
            "ch": "chi_sim+eng",
            "en": "eng",
            "chinese": "chi_sim+eng",
            "english": "eng",
        }
        self.lang = lang_map.get(lang.lower(), "chi_sim+eng")

        if os.path.exists(TESSERACT_PATH):
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

        self._current_image = None
        self._current_gray = None

        if LAYOUT_ANALYZER_AVAILABLE and getattr(
            config, "ENABLE_LAYOUT_ANALYSIS", False
        ):
            self.layout_analyzer = LayoutAnalyzer()
        else:
            self.layout_analyzer = None

    def process_image(self, image) -> List[Dict]:
        if hasattr(image, "mode"):
            image_np = np.array(image.convert("RGB"))
        else:
            image_np = image

        self._current_image = image_np
        self._current_gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        if self.layout_analyzer:
            return self._process_with_layout_analysis(image_np)
        else:
            return self._process_without_layout(image_np)

    def _process_with_layout_analysis(self, image_np: np.ndarray) -> List[Dict]:
        layout_regions = self.layout_analyzer.analyze_layout(image_np)

        all_texts = []

        for region in layout_regions:
            bbox = region["bbox"]
            x, y, w, h = bbox
            image_regions = region.get("image_regions", [])

            x = max(0, x)
            y = max(0, y)
            x_end = min(x + w, image_np.shape[1])
            y_end = min(y + h, image_np.shape[0])

            if x_end <= x or y_end <= y:
                continue

            region_img = image_np[y:y_end, x:x_end]

            try:
                data = pytesseract.image_to_data(
                    region_img,
                    lang=self.lang,
                    output_type=pytesseract.Output.DICT,
                    config="--psm 6",
                )
            except Exception as e:
                continue

            n_boxes = len(data["text"])

            for i in range(n_boxes):
                text = data["text"][i].strip()
                confidence = float(data["conf"][i])

                if not text or confidence < 0:
                    continue

                tx, ty, tw, th = (
                    data["left"][i],
                    data["top"][i],
                    data["width"][i],
                    data["height"][i],
                )

                if tw < 5 or th < 5:
                    continue

                abs_x = x + tx
                abs_y = y + ty
                block_bbox = (abs_x, abs_y, tw, th)

                if image_regions and not self.layout_analyzer.is_text_block(
                    block_bbox, image_regions
                ):
                    continue

                all_texts.append(
                    self._create_text_dict(
                        text=text,
                        confidence=confidence / 100.0,
                        x_min=float(abs_x),
                        y_min=float(abs_y),
                        width=float(tw),
                        height=float(th),
                        image_np=image_np,
                        layout_info={
                            "page_index": region.get("page_index", 1),
                            "column_index": region.get("column_index", 1),
                            "region_type": region.get("type", "column"),
                        },
                    )
                )

        all_texts.sort(
            key=lambda x: (
                x["layout_info"]["page_index"],
                x["layout_info"]["column_index"],
                x["y_position"],
                x["bbox"][0],
            )
        )

        return all_texts

    def _process_without_layout(self, image_np: np.ndarray) -> List[Dict]:
        try:
            data = pytesseract.image_to_data(
                image_np,
                lang=self.lang,
                output_type=pytesseract.Output.DICT,
                config="--psm 6",
            )
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return []

        texts_with_style = []
        n_boxes = len(data["text"])

        for i in range(n_boxes):
            text = data["text"][i].strip()
            confidence = float(data["conf"][i])

            if not text or confidence < 0:
                continue

            x, y, w, h = (
                data["left"][i],
                data["top"][i],
                data["width"][i],
                data["height"][i],
            )

            if w < 5 or h < 5:
                continue

            texts_with_style.append(
                self._create_text_dict(
                    text=text,
                    confidence=confidence / 100.0,
                    x_min=float(x),
                    y_min=float(y),
                    width=float(w),
                    height=float(h),
                    image_np=image_np,
                )
            )

        texts_with_style.sort(key=lambda x: (x["y_position"], x["bbox"][0]))
        return texts_with_style

    def _create_text_dict(
        self,
        text: str,
        confidence: float,
        x_min: float,
        y_min: float,
        width: float,
        height: float,
        image_np: np.ndarray,
        layout_info: Dict = None,
    ) -> Dict:
        img_height, img_width = image_np.shape[:2]
        text_center_x = x_min + width / 2
        page_center = img_width / 2

        if abs(text_center_x - page_center) < width * 0.3:
            alignment = "center"
        elif text_center_x < page_center:
            alignment = "left"
        else:
            alignment = "right"

        text_region = None
        try:
            text_region = self._current_gray[
                int(max(0, y_min)) : int(min(img_height, y_min + height)),
                int(max(0, x_min)) : int(min(img_width, x_min + width)),
            ]
        except (IndexError, ValueError):
            pass

        result = {
            "text": text,
            "confidence": confidence,
            "position": [
                [x_min, y_min],
                [x_min + width, y_min],
                [x_min + width, y_min + height],
                [x_min, y_min + height],
            ],
            "bbox": (x_min, y_min, width, height),
            "font_size": height,
            "text_width": width,
            "alignment": alignment,
            "y_position": y_min,
            "text_region": text_region
            if text_region is not None and text_region.size > 0
            else None,
        }

        if layout_info:
            result["layout_info"] = layout_info
        else:
            result["layout_info"] = {
                "page_index": 1,
                "column_index": 1,
                "region_type": "single",
            }

        return result

    def classify_text_style(
        self, text_info: Dict, min_heading_size: int = None
    ) -> Dict:
        font_size = text_info["font_size"]
        alignment = text_info["alignment"]
        text = text_info["text"]
        text_region = text_info.get("text_region")

        if min_heading_size is None:
            min_heading_size = getattr(config, "MIN_HEADING_FONT_SIZE", 24)

        heading_levels = getattr(
            config, "HEADING_SIZE_LEVELS", {1: 48, 2: 36, 3: 28, 4: 24}
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

        if text_region is not None and text_region.size > 0:
            styles["is_bold"] = self._detect_bold(text_region, text, font_size)
            styles["is_italic"] = self._detect_italic(text_region)

        list_patterns = [
            ("bullet", r"^[\*\•\-\→]\s+"),
            ("numbered", r"^\d+[\.\)]\s+"),
            ("lettered", r"^[a-zA-Z][\.\)]\s+"),
        ]

        for list_type, pattern in list_patterns:
            if re.match(pattern, text.strip()):
                styles["is_list"] = True
                styles["list_type"] = list_type
                break

        if styles["is_heading"] and styles["heading_level"]:
            styles["markdown_prefix"] = "#" * styles["heading_level"] + " "
        elif styles["is_list"]:
            list_type = styles.get("list_type", "bullet")
            if list_type == "bullet":
                styles["markdown_prefix"] = "- "
            elif list_type == "numbered":
                styles["markdown_prefix"] = "1. "
            elif list_type == "lettered":
                styles["markdown_prefix"] = "a. "

        if styles["is_bold"] and styles["is_italic"]:
            styles["markdown_prefix"] += "***"
            styles["markdown_suffix"] = "***"
        elif styles["is_bold"]:
            styles["markdown_prefix"] += "**"
            styles["markdown_suffix"] = "**"
        elif styles["is_italic"]:
            styles["markdown_prefix"] += "*"
            styles["markdown_suffix"] = "*"

        if styles["is_centered"] and not styles["is_heading"]:
            styles["markdown_prefix"] = "<center>" + styles["markdown_prefix"]
            styles["markdown_suffix"] = styles["markdown_suffix"] + "</center>"

        return styles

    def _detect_bold(
        self, text_region: np.ndarray, text: str, font_size: float = None
    ) -> bool:
        try:
            _, binary = cv2.threshold(
                text_region, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )
            dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)

            if np.sum(binary > 0) == 0:
                return False

            avg_stroke_width = np.mean(dist_transform[binary > 0])
            pixel_density = np.sum(binary > 0) / binary.size
            height = text_region.shape[0]

            # Normalize stroke width relative to text height
            normalized_stroke = avg_stroke_width / height if height > 0 else 0

            # Multi-factor detection for better accuracy
            stroke_threshold = getattr(config, "BOLD_STROKE_RATIO", 0.15)
            density_threshold = getattr(config, "BOLD_PIXEL_DENSITY", 0.4)
            min_area = getattr(config, "BOLD_MIN_AREA", 100)

            # Filter out very small regions (noise)
            if binary.size < min_area:
                return False

            # Primary detection: stroke analysis
            stroke_score = normalized_stroke > stroke_threshold

            # Secondary detection: pixel density (backup method)
            density_score = pixel_density > density_threshold

            # Tertiary: check for consistent thick strokes across region
            stroke_var = (
                np.var(dist_transform[binary > 0]) if np.sum(binary > 0) > 0 else 0
            )
            consistency_score = stroke_var < (avg_stroke_width * 0.5)

            # Weighted decision (requires 2 out of 3 methods)
            decision = int(stroke_score) + int(density_score) + int(consistency_score)

            return decision >= 2
        except Exception:
            return False

    def _detect_italic(self, text_region: np.ndarray) -> bool:
        try:
            _, binary = cv2.threshold(
                text_region, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )

            if binary.size == 0 or np.sum(binary) == 0:
                return False

            contours, _ = cv2.findContours(
                binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if not contours:
                return False

            # Improved angle detection with outlier filtering
            slant_angles = []
            min_pixel_area = 50  # Minimum contour area to consider

            for contour in contours:
                if len(contour) < 5:
                    continue

                area = cv2.contourArea(contour)
                if area < min_pixel_area:
                    continue

                try:
                    ellipse = cv2.fitEllipse(contour)
                    angle = ellipse[2]

                    # Normalize angle to [-90, 90]
                    if angle > 90:
                        angle -= 180
                    elif angle < -90:
                        angle += 180

                    # Filter extreme angles (likely noise or rotated text)
                    if -80 < angle < 80:
                        slant_angles.append(angle)
                except cv2.error:
                    continue

            if not slant_angles:
                return False

            # Use median instead of mean to reduce outlier impact
            median_slant = np.median(slant_angles)

            # Configurable thresholds
            min_angle = getattr(config, "ITALIC_MIN_ANGLE", 10)
            max_angle = getattr(config, "ITALIC_MAX_ANGLE", 45)

            # Check if most contours show consistent slant
            in_range_count = sum(
                1 for a in slant_angles if min_angle < abs(a) < max_angle
            )
            consistency_ratio = in_range_count / len(slant_angles)

            # Require at least 60% of contours to show slant
            is_italic = (min_angle < abs(median_slant) < max_angle) and (
                consistency_ratio > 0.6
            )

            return is_italic
        except Exception:
            return False

    def group_text_lines(
        self, texts: List[Dict], y_threshold: float = 15, respect_layout: bool = True
    ) -> List[Dict]:
        """
        Group text blocks into lines based on y-position.

        Args:
            texts: List of text dictionaries from OCR
            y_threshold: Maximum y-distance to consider same line
            respect_layout: If True, group separately by page/column (prevents mixing)

        Returns:
            List of merged text line dictionaries
        """
        if not texts:
            return []

        if respect_layout:
            # Group by (page_index, column_index) first to prevent cross-column mixing
            layout_groups = {}
            for text in texts:
                layout_info = text.get("layout_info", {})
                page_idx = layout_info.get("page_index", 1)
                col_idx = layout_info.get("column_index", 1)
                key = (page_idx, col_idx)
                if key not in layout_groups:
                    layout_groups[key] = []
                layout_groups[key].append(text)

            # Process each layout group separately
            all_grouped = []
            for key in sorted(layout_groups.keys()):
                group_texts = layout_groups[key]
                # Sort by y-position, then x-position within each group
                group_texts.sort(key=lambda x: (x["y_position"], x["bbox"][0]))
                grouped = self._group_single_layout(group_texts, y_threshold)
                all_grouped.extend(grouped)

            return all_grouped
        else:
            # Original behavior: sort all by y then group
            texts.sort(key=lambda x: (x["y_position"], x["bbox"][0]))
            return self._group_single_layout(texts, y_threshold)

    def _group_single_layout(
        self, texts: List[Dict], y_threshold: float = 15
    ) -> List[Dict]:
        """Group texts within a single layout region (same page/column)."""
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
        """Merge text blocks into a single line with smart horizontal gap handling."""
        if len(line_texts) == 1:
            return line_texts[0]

        # Sort by x-position for proper ordering
        line_texts = sorted(line_texts, key=lambda x: x["bbox"][0])

        # Calculate average font size for gap threshold
        avg_font_size = sum(t.get("font_size", 20) for t in line_texts) / len(line_texts)
        horizontal_gap_threshold = avg_font_size * 1.5  # Allow gaps up to 1.5x font size

        # Merge with smart horizontal gap handling
        text_parts = []
        prev_x_end = None

        for text_info in line_texts:
            text = text_info["text"].strip()
            x, y, w, h = text_info["bbox"]
            x_end = x + w

            if prev_x_end is not None:
                gap = x - prev_x_end
                # Use single space if gap is small enough, otherwise add extra spacing
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
            "text_region": first_text.get("text_region"),
            "layout_info": first_text.get(
                "layout_info", {"page_index": 1, "column_index": 1}
            ),
        }
