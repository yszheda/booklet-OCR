import sys
sys.path.insert(0, "src")
import cv2
import numpy as np
from PIL import Image as P

from ocr_processor import BookletOCR
from image_utils import load_image

img = load_image("testcases/HIPPO_20220124_0004.jpg")
img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

ocr = BookletOCR(lang="en")
results = ocr.process_image(img_np)

# Find potential title components (y around 80-95, large width)
print("Title area candidates (y=75-100, w>400):")
title_candidates = []
for r in results:
    y = r.get("y_position", 0)
    w = r.get("bbox", (0,0,0,0))[2]
    text = r.get("text", "")
    if 75 <= y <= 100 and w > 400:
        title_candidates.append((y, w, text))

title_candidates.sort(key=lambda x: x[0])
for y, w, text in title_candidates:
    print(f"y={y} w={w} | {text}")
