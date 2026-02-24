import cv2
import numpy as np
import sys
sys.path.insert(0, ".")
from layout_analyzer import LayoutAnalyzer

img = cv2.imread("testcases/HIPPO_20220124_0004.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
analyzer = LayoutAnalyzer()

print("Testing column detection on test image")
print("="*60)

# Test column detection
columns = analyzer.detect_columns(gray, max_columns=3)
print(f"\nDetected {len(columns)} columns:")
for i, col in enumerate(columns, 1):
    (x_start, y_start, width, height) = col.get("bbox", (0,0,0,0))
    print(f"  Col {i}: x={x_start}, y={y_start}, w={width}, h={height}")

# Analyze first 50 text items from OCR
print("\nFirst 50 OCR text items sorted by x-position:")
sys.path.insert(0, "src")
from ocr_processor import BookletOCR
from image_utils import load_image
import cv2

ocr = BookletOCR(lang="en")
img = load_image("testcases/HIPPO_20220124_0004.jpg")
img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
results = ocr.process_image(img_np)

sorted_x = sorted(results, key=lambda x: x.get("bbox", (0,0,0,0))[0])
for i, r in enumerate(sorted_x[:50], 1):
    x = r.get("bbox", (0,0,0,0))[0]
    text = r.get("text", "")[:50]
    print(f"  {i}. x={x:4d} | {text}")
