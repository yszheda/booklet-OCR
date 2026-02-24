#!/usr/bin/env python
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ocr_backends import create_ocr_backend
import cv2

test_image = Path(__file__).parent.parent / "testcases" / "HIPPO_20220124_0004.jpg"
print(f"Testing OCR engines on {test_image.name}\n")

test_track_patterns = []
for i in range(1, 21):
    test_track_patterns.append(f"Contrapunctus {i}")
test_track_patterns.extend(["Canon per augmentationem", "Canon alla ottava", 
                           "Canon alla decima", "Canon alla duodecima"])

for engine_name in ["tesseract"]:
    try:
        engine = create_ocr_backend(backend=engine_name, lang="en")
        img = cv2.imread(str(test_image))
        results = engine.process_image(img)
        
        print(f"[{engine_name.upper()}] Total: {len(results)} items")
        
        tracks_found = 0
        for r in results:
            text = r.get('text', '')
            for pattern in test_track_patterns:
                if pattern in text:
                    tracks_found += 1
                    print(f"  Track found: {text[:60]}")
                    break
        
        if tracks_found > 0:
            print(f"  Found {tracks_found}/20 track items")
        print()
    except Exception as e:
        print(f"[{engine_name.upper()}] ERROR: {e}\n")
