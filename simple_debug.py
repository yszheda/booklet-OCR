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

sorted_y = sorted(results, key=lambda x: x["y_position"])

print("Looking at items around track 6 (should be y~60-90):")
y_range = [50, 95]
for i, r in enumerate(sorted_y):
    y = r.get("y_position", 0)
    if y_range[0] <= y <= y_range[1]:
        x = r.get("bbox", (0,0,0,0))[0]
        w = r.get("bbox", (0,0,0,0))[2]
        text = r.get("text", "")
        print(f"[{i}] y={y} x={x} w={w} | {text}")
