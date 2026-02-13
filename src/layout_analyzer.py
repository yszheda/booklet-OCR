"""Layout analysis for multi-page detection, column identification, and image filtering

This module handles:
1. Multi-page detection: Detect if an image contains multiple scanned pages
2. Column detection: Identify multi-column layouts (like newspapers)
3. Image region filtering: Exclude non-text (image) regions from OCR
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path


class LayoutAnalyzer:
    def __init__(self):
        self.min_text_area_config = 1000
        self.min_line_length_config = 50
        self.page_split_threshold = 0.3
        self.column_gap_threshold = 100
        # Image region detection thresholds
        self.image_region_min_area = 5000  # Minimum area for image region
        self.text_density_min = 0.02  # Minimum text density for text region
        self.text_density_max = 0.85  # Maximum density (solid blocks are images)

    def detect_pages(
        self, image: np.ndarray, vertical_proj_threshold: float = 0.1
    ) -> List[Dict]:
        gray = (
            cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        )

        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        vertical_proj = np.sum(binary, axis=1)
        normalized_proj = vertical_proj / (binary.shape[1])

        min_gap_height = image.shape[0] * 0.15

        gaps = []
        in_gap = False
        gap_start = 0

        for y in range(len(normalized_proj)):
            is_gap = normalized_proj[y] < vertical_proj_threshold * 0.5

            if is_gap and not in_gap:
                in_gap = True
                gap_start = y
            elif not is_gap and in_gap:
                in_gap = False
                gap_height = y - gap_start
                if gap_height >= min_gap_height:
                    gaps.append((gap_start, y))

        if not gaps:
            return [
                {"type": "single_page", "bbox": (0, 0, image.shape[1], image.shape[0])}
            ]

        pages = []
        prev_end = 0

        for gap_start, gap_end in gaps:
            if gap_start > prev_end + image.shape[0] * 0.1:
                pages.append(
                    {
                        "type": "page",
                        "index": len(pages) + 1,
                        "bbox": (0, prev_end, image.shape[1], gap_start),
                    }
                )
            prev_end = gap_end

        if image.shape[0] - prev_end > image.shape[0] * 0.1:
            pages.append(
                {
                    "type": "page",
                    "index": len(pages) + 1,
                    "bbox": (0, prev_end, image.shape[1], image.shape[0]),
                }
            )

        if not pages:
            pages = [
                {"type": "single_page", "bbox": (0, 0, image.shape[1], image.shape[0])}
            ]

        return pages

    def detect_columns(
        self, page_image: np.ndarray, min_columns: int = 1, max_columns: int = 3
    ) -> List[Dict]:
        gray = (
            cv2.cvtColor(page_image, cv2.COLOR_RGB2GRAY)
            if len(page_image.shape) == 3
            else page_image
        )

        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        horizontal_proj = np.sum(binary, axis=0)
        width = page_image.shape[1]
        height = page_image.shape[0]

        max_proj = np.max(horizontal_proj) if np.max(horizontal_proj) > 0 else 1
        normalized_proj = horizontal_proj / max_proj

        min_gap_width = width * 0.03

        gaps = []
        in_gap = False
        gap_start = 0
        gap_threshold = 0.15

        for x in range(width):
            is_gap = normalized_proj[x] < gap_threshold

            if is_gap and not in_gap:
                in_gap = True
                gap_start = x
            elif not is_gap and in_gap:
                in_gap = False
                gap_width = x - gap_start
                if gap_width >= min_gap_width:
                    center = (gap_start + x) // 2
                    gaps.append((gap_start, x, gap_width, center))

        if not gaps:
            return [
                {
                    "type": "column",
                    "index": 1,
                    "bbox": (0, 0, page_image.shape[1], page_image.shape[0]),
                }
            ]

        center_of_image = width // 2
        candidate_gaps = []
        for gap in gaps:
            gap_center = gap[3]
            distance_to_center = abs(gap_center - center_of_image)
            if distance_to_center < width * 0.25:
                candidate_gaps.append(gap)

        if not candidate_gaps:
            candidate_gaps = gaps

        candidate_gaps.sort(key=lambda x: x[2], reverse=True)
        best_splits = candidate_gaps[: max_columns - 1]
        best_splits.sort(key=lambda x: x[0])

        x_boundaries = [0] + [gap[3] for gap in best_splits] + [width]

        columns = []
        col_index = 1
        for i in range(len(x_boundaries) - 1):
            x_start = x_boundaries[i]
            x_end = x_boundaries[i + 1]
            column_width = x_end - x_start

            if column_width > width * 0.15:
                columns.append(
                    {
                        "type": "column",
                        "index": col_index,
                        "bbox": (x_start, 0, column_width, height),
                    }
                )
                col_index += 1

        if not columns:
            columns = [
                {
                    "type": "column",
                    "index": 1,
                    "bbox": (0, 0, page_image.shape[1], page_image.shape[0]),
                }
            ]

        return columns

    def detect_image_regions(
        self, image: np.ndarray, min_area: int = None
    ) -> List[Dict]:
        """
        Detect large image/graphics regions that should be excluded from text OCR.
        Image regions typically have: large area, low text density, or solid colors.
        """
        if min_area is None:
            min_area = self.image_region_min_area

        gray = (
            cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        )

        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))
        dilated = cv2.dilate(binary, kernel, iterations=2)

        contours, _ = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        image_regions = []
        total_image_area = image.shape[0] * image.shape[1]

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h

            if area < min_area:
                continue

            region = gray[y : y + h, x : x + w]
            _, region_binary = cv2.threshold(
                region, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )

            density = np.sum(region_binary > 0) / region_binary.size

            area_ratio = area / total_image_area

            is_solid_block = density > self.text_density_max
            is_very_large_photo = area_ratio > 0.3 and density < 0.08
            is_solid_color = density < 0.01

            if is_solid_block or is_very_large_photo or is_solid_color:
                aspect_ratio = w / h if h > 0 else 0
                image_regions.append(
                    {
                        "type": "image",
                        "bbox": (x, y, w, h),
                        "density": density,
                        "area": area,
                        "aspect_ratio": aspect_ratio,
                    }
                )

        return image_regions

    def is_text_block(
        self, block_bbox: Tuple, image_regions: List[Dict], threshold: float = 0.5
    ) -> bool:
        """Check if a text block overlaps with detected image regions."""
        bx, by, bw, bh = block_bbox
        block_area = bw * bh

        for img_region in image_regions:
            ix, iy, iw, ih = img_region["bbox"]

            x_overlap = max(0, min(bx + bw, ix + iw) - max(bx, ix))
            y_overlap = max(0, min(by + bh, iy + ih) - max(by, iy))
            overlap_area = x_overlap * y_overlap

            if overlap_area > 0:
                overlap_ratio = overlap_area / block_area
                if overlap_ratio > threshold:
                    return False

        return True

    def filter_image_regions(
        self,
        column_image: np.ndarray,
        text_blocks: List[Dict],
        min_text_density: float = 0.05,
    ) -> List[Dict]:
        column_area = column_image.shape[0] * column_image.shape[1]

        total_text_pixels = 0
        for block in text_blocks:
            bbox = block.get("bbox", (0, 0, 0, 0))
            total_text_pixels += bbox[2] * bbox[3]

        if column_area > 0:
            text_density = total_text_pixels / column_area
            if text_density < min_text_density:
                return []

        filtered_blocks = []
        for block in text_blocks:
            bbox = block.get("bbox", (0, 0, 0, 0))
            x, y, w, h = bbox

            if w * h < self.min_text_area_config:
                continue

            if w < 10 or h < 5:
                continue

            x_end = min(x + w, column_image.shape[1])
            y_end = min(y + h, column_image.shape[0])

            region = column_image[y:y_end, x:x_end]
            if len(region.shape) == 3:
                region_gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
            else:
                region_gray = region

            _, region_binary = cv2.threshold(
                region_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )

            region_density = np.sum(region_binary > 0) / region_binary.size

            if region_density > 0.01 and region_density < 0.95:
                filtered_blocks.append(block)

        return filtered_blocks

    def analyze_layout(self, image: np.ndarray) -> List[Dict]:
        pages = self.detect_pages(image)

        analyzed = []

        for page_info in pages:
            page_bbox = page_info["bbox"]
            px, py, pw, ph = page_bbox

            page_region = image[py : py + ph, px : px + pw]

            image_regions = self.detect_image_regions(page_region)

            columns = self.detect_columns(page_region)

            for col_info in columns:
                col_bbox = col_info["bbox"]
                cx, cy, cw, ch = col_bbox

                col_absolute_bbox = (
                    px + cx,
                    py + cy,
                    cw,
                    ch,
                )

                col_image_regions = []
                for ir in image_regions:
                    ir_x, ir_y, ir_w, ir_h = ir["bbox"]

                    ir_in_col_x = max(0, ir_x - cx)
                    ir_in_col_y = max(0, ir_y - cy)
                    ir_in_col_w = (
                        min(ir_w, cx + cw - ir_x)
                        if ir_x >= cx
                        else min(ir_x + ir_w - cx, cw)
                    )
                    ir_in_col_h = (
                        min(ir_h, cy + ch - ir_y)
                        if ir_y >= cy
                        else min(ir_y + ir_h - cy, ch)
                    )

                    x_overlap = max(0, min(cx + cw, ir_x + ir_w) - max(cx, ir_x))
                    y_overlap = max(0, min(cy + ch, ir_y + ir_h) - max(cy, ir_y))

                    if x_overlap > 0 and y_overlap > 0:
                        ir_area = ir_w * ir_h
                        overlap_area = x_overlap * y_overlap

                        if overlap_area > ir_area * 0.3:
                            col_image_regions.append({"bbox": (ir_x, ir_y, ir_w, ir_h)})

                analyzed.append(
                    {
                        "type": "column",
                        "page_index": page_info.get("index", 1),
                        "column_index": col_info["index"],
                        "bbox": col_absolute_bbox,
                        "image_regions": col_image_regions,
                    }
                )

        return analyzed

    def extract_text_regions(
        self, image: np.ndarray, layout_regions: List[Dict], method: str = "contour"
    ) -> List[Dict]:
        text_regions = []

        for region in layout_regions:
            bbox = region["bbox"]
            x, y, w, h = bbox

            x = max(0, x)
            y = max(0, y)
            x_end = min(x + w, image.shape[1])
            y_end = min(y + h, image.shape[0])

            if x_end <= x or y_end <= y:
                continue

            region_img = image[y:y_end, x:x_end]

            if method == "contour":
                regions = self._extract_by_contours(region_img)
            elif method == "projection":
                regions = self._extract_by_projection(region_img)
            else:
                regions = self._extract_by_contours(region_img)

            for reg in regions:
                abs_bbox = (
                    x + reg["bbox"][0],
                    y + reg["bbox"][1],
                    reg["bbox"][2],
                    reg["bbox"][3],
                )

                reg["absolute_bbox"] = abs_bbox
                reg["page_index"] = region.get("page_index", 1)
                reg["column_index"] = region.get("column_index", 1)

                text_regions.append(reg)

        return text_regions

    def _extract_by_contours(self, region_image: np.ndarray) -> List[Dict]:
        if len(region_image.shape) == 3:
            gray = cv2.cvtColor(region_image, cv2.COLOR_RGB2GRAY)
        else:
            gray = region_image

        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            if w * h < self.min_text_area_config:
                continue

            if w < 5 or h < 5:
                continue

            extent = cv2.contourArea(contour) / (w * h)
            if extent < 0.3:
                continue

            aspect_ratio = w / h if h > 0 else 0
            if aspect_ratio > 20 or aspect_ratio < 0.05:
                continue

            regions.append(
                {
                    "type": "text_region",
                    "bbox": (x, y, w, h),
                    "confidence": 1.0,
                }
            )

        regions.sort(key=lambda r: (r["bbox"][1], r["bbox"][0]))

        return regions

    def _extract_by_projection(self, region_image: np.ndarray) -> List[Dict]:
        if len(region_image.shape) == 3:
            gray = cv2.cvtColor(region_image, cv2.COLOR_RGB2GRAY)
        else:
            gray = region_image

        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        horizontal_proj = np.sum(binary, axis=1)

        regions = []
        in_text = False
        y_start = 0

        for y in range(len(horizontal_proj)):
            if horizontal_proj[y] > 0:
                if not in_text:
                    y_start = y
                    in_text = True
            else:
                if in_text and y - y_start > 5:
                    h = y - y_start
                    if h > 5:
                        x_proj = np.sum(binary[y_start:y, :], axis=0)

                        x_start = 0
                        x_end = len(x_proj)

                        for i in range(len(x_proj)):
                            if x_proj[i] > 0:
                                x_start = i
                                break

                        for i in range(len(x_proj) - 1, -1, -1):
                            if x_proj[i] > 0:
                                x_end = i + 1
                                break

                        w = x_end - x_start

                        if w > 10:
                            regions.append(
                                {
                                    "type": "text_region",
                                    "bbox": (x_start, y_start, w, h),
                                    "confidence": 1.0,
                                }
                            )

                    in_text = False

        if in_text and len(horizontal_proj) - y_start > 5:
            h = len(horizontal_proj) - y_start
            if h > 5:
                regions.append(
                    {
                        "type": "text_region",
                        "bbox": (0, y_start, region_image.shape[1], h),
                        "confidence": 1.0,
                    }
                )

        regions.sort(key=lambda r: (r["bbox"][1], r["bbox"][0]))

        return regions
