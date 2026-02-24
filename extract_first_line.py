import sys
sys.path.insert(0, "src")
from pathlib import Path
import cv2
import numpy as np

from ocr_processor import BookletOCR
from image_utils import load_image
import config

test_file = Path("testcases/HIPPO_20220124_0004.jpg")
img = load_image(test_file)
img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

ocr = BookletOCR(lang="en")
results = ocr.process_image(img_np)

print("Raw items with y around 60-90 (曲目1 area):")
for r in results:
    y = r.get("y_position", 0)
    if 45 <= y <= 95:
        x = r.get("bbox", (0,0,0,0))[0]
        w = r.get("bbox", (0,0,0,0))[2]
        text = r.get("text", "")
        print(f"y={y:3d} x={x:4d} w={w:3d} | {text}")
