#!/usr/bin/env python
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ocr_backends import create_ocr_backend
import cv2
import re

test_image = Path(__file__).parent.parent / "testcases" / "HIPPO_20220124_0004.jpg"

def test_rapidocr():
    engine = create_ocr_backend(backend="rapidocr", lang="en")
    img = cv2.imread(str(test_image))
    results = engine.process_image(img)
    
    print(f"RapidOCR detected {len(results)} text items\n")
    
    tracks = []
    for r in results:
        text = r.get('text', '')
        track_match = re.match(r"(\d+)\s+(.+)", text)
        if track_match:
            tracks.append(text)
        elif "Canon" in text or "Contrapunctus" in text:
            tracks.append(text)
    
    print("Detected track items:")
    for i, t in enumerate(tracks, 1):
        print(f"  {i}. {t[:70]}")
    
    time_found = 0
    for r in results:
        text = r.get('text', '')
        if re.search(r"\{\d+:\d+\}", text) or re.search(r"\{", text):
            time_found += 1
            print(f"\nTime marker found: {text}")
    
    return results

if __name__ == "__main__":
    results = test_rapidocr()
