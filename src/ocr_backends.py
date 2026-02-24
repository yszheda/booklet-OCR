"""OCR Backend Factory - Support multiple OCR engines"""

from typing import List, Dict
import sys
from pathlib import Path

import cv2
import numpy as np


def create_ocr_backend(backend: str = "tesseract", lang: str = "en"):
    """Factory function to create OCR backend"""

    if backend == "rapidocr":
        return RapidOCREngine(lang)
    elif backend == "easyocr":
        return EasyOCREngine(lang)
    elif backend == "paddleocr":
        return PaddleOCREngine(lang)
    elif backend == "tesseract":
        return TesseractEngine(lang)
    else:
        raise ValueError(f"Unknown OCR backend: {backend}")


class BaseOCREngine:
    """Base class for OCR engines"""

    def __init__(self, lang: str):
        self.lang = lang

    def process_image(self, image: np.ndarray) -> List[Dict]:
        """Process image and return text results"""
        raise NotImplementedError


class RapidOCREngine(BaseOCREngine):
    """RapidOCR backend - fast and accurate for printed text"""

    def __init__(self, lang: str):
        super().__init__(lang)
        self.reader = None
        self._initialize()

    def _initialize(self):
        try:
            from rapidocr_onnxruntime import RapidOCR as _RapidOCR

            self.reader = _RapidOCR()
            print(f"OK RapidOCR initialized (lang={self.lang})")
        except ImportError:
            print("FAIL RapidOCR not installed. Run: pip install rapidocr-onnxruntime")
            self.reader = None

    def process_image(self, image: np.ndarray) -> List[Dict]:
        if self.reader is None:
            return []

        try:
            result = self.reader(image)
            texts = []

            if result and result[0]:
                for item in result[0]:
                    points, (text, confidence) = item

                    x_coords = [p[0] for p in points]
                    y_coords = [p[1] for p in points]

                    x_min = int(min(x_coords))
                    y_min = int(min(y_coords))
                    x_max = int(max(x_coords))
                    y_max = int(max(y_coords))

                    texts.append(
                        {
                            "text": text,
                            "confidence": float(confidence),
                            "bbox": (x_min, y_min, x_max - x_min, y_max - y_min),
                            "font_size": int((y_max - y_min) * 0.75),
                            "text_width": x_max - x_min,
                            "alignment": "left",
                            "y_position": y_min,
                            "text_region": None,
                            "layout_info": {"page_index": 1, "column_index": 1},
                            "position": points,
                        }
                    )

            return texts
        except Exception as e:
            print(f"Error in RapidOCR: {e}")
            return []


class EasyOCREngine(BaseOCREngine):
    """EasyOCR backend - deep learning based, multilingual"""

    def __init__(self, lang: str):
        super().__init__(lang)
        self.reader = None
        self._initialize()

    def _initialize(self):
        try:
            import easyocr

            # Map language codes
            lang_map = {"en": "en", "ch": "ch_sim"}
            ocr_lang = lang_map.get(self.lang, "en")
            self.reader = easyocr.Reader([ocr_lang], gpu=False)
            print(f"OK EasyOCR initialized (lang={ocr_lang})")
        except ImportError:
            print("FAIL EasyOCR not installed. Run: pip install easyocr")
            self.reader = None

    def process_image(self, image: np.ndarray) -> List[Dict]:
        if self.reader is None:
            return []

        try:
            results = self.reader.readtext(image)
            texts = []

            for bbox, text, confidence in results:
                bbox = np.array(bbox).astype(np.int32)
                x_min = int(bbox[:, 0].min())
                y_min = int(bbox[:, 1].min())
                x_max = int(bbox[:, 0].max())
                y_max = int(bbox[:, 1].max())

                texts.append(
                    {
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": (x_min, y_min, x_max - x_min, y_max - y_min),
                        "font_size": int((y_max - y_min) * 0.75),
                        "text_width": x_max - x_min,
                        "alignment": "left",
                        "y_position": y_min,
                        "text_region": None,
                        "layout_info": {"page_index": 1, "column_index": 1},
                        "position": bbox.tolist(),
                    }
                )

            return texts
        except Exception as e:
            print(f"Error in EasyOCR: {e}")
            return []


class PaddleOCREngine(BaseOCREngine):
    """PaddleOCR backend - best for Chinese text"""

    def __init__(self, lang: str):
        super().__init__(lang)
        self.reader = None
        self._initialize()

    def _initialize(self):
        try:
            from paddleocr import PaddleOCR as _PaddleOCR

            # Map language codes
            lang_map = {"en": "en", "ch": "ch"}
            ocr_lang = lang_map.get(self.lang, "en")
            self.reader = _PaddleOCR(use_angle_cls=True, lang=ocr_lang, show_log=False)
            print(f"OK PaddleOCR initialized (lang={ocr_lang})")
        except ImportError:
            print("FAIL PaddleOCR not installed. Run: pip install paddleocr")
            self.reader = None

    def process_image(self, image: np.ndarray) -> List[Dict]:
        if self.reader is None:
            return []

        try:
            result = self.reader.ocr(image, cls=True)
            texts = []

            if result and result[0]:
                for line in result[0]:
                    bbox = np.array(line[0]).astype(np.int32)
                    text_info = line[1][0]
                    confidence = line[1][1]

                    x_min = int(bbox[:, 0].min())
                    y_min = int(bbox[:, 1].min())
                    x_max = int(bbox[:, 0].max())
                    y_max = int(bbox[:, 1].max())

                    texts.append(
                        {
                            "text": text_info,
                            "confidence": float(confidence),
                            "bbox": (x_min, y_min, x_max - x_min, y_max - y_min),
                            "font_size": int((y_max - y_min) * 0.75),
                            "text_width": x_max - x_min,
                            "alignment": "left",
                            "y_position": y_min,
                            "text_region": None,
                            "layout_info": {"page_index": 1, "column_index": 1},
                            "position": bbox.tolist(),
                        }
                    )

            return texts
        except Exception as e:
            print(f"Error in PaddleOCR: {e}")
            return []


class TesseractEngine(BaseOCREngine):
    """Tesseract backend - traditional OCR"""

    def __init__(self, lang: str):
        super().__init__(lang)
        self.reader = None
        self._initialize()

    def _initialize(self):
        try:
            import pytesseract

            self.pytesseract = pytesseract
            print(f"OK Tesseract initialized (lang={self.lang})")
        except ImportError:
            print("FAIL pytesseract not installed. Run: pip install pytesseract")
            self.reader = None

    def process_image(self, image: np.ndarray) -> List[Dict]:
        try:
            import pytesseract

            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            texts = []
            for i in range(len(data["text"])):
                text = data["text"][i].strip()
                if not text or int(data["conf"][i]) < 0:
                    continue

                texts.append(
                    {
                        "text": text,
                        "confidence": float(data["conf"][i]) / 100,
                        "bbox": (
                            data["left"][i],
                            data["top"][i],
                            data["width"][i],
                            data["height"][i],
                        ),
                        "font_size": int(data["height"][i] * 0.9),
                        "text_width": data["width"][i],
                        "alignment": "left",
                        "y_position": data["top"][i],
                        "text_region": None,
                        "layout_info": {"page_index": 1, "column_index": 1},
                        "position": None,
                    }
                )

            return texts
        except Exception as e:
            print(f"Error in Tesseract: {e}")
            return []


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        choices=["tesseract", "rapidocr", "easyocr", "paddleocr"],
        default="rapidocr",
    )
    parser.add_argument("--image", help="Path to test image")
    args = parser.parse_args()

    engine = create_ocr_backend(backend=args.backend, lang="en")

    if args.image:
        img = cv2.imread(args.image)
        if img is not None:
            results = engine.process_image(img)
            print(f"\nFound {len(results)} text items:")
            for i, r in enumerate(results[:10], 1):
                print(f"  {i}. [{r['confidence']:.2f}] {r['text']}")
