# Quick script to analyze title issue
import sys
sys.path.insert(0, '.')
from ocr_processor import BookletOCR
from image_utils import load_image
import cv2

img = load_image('testcases/HIPPO_20220124_0004.jpg')
img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
ocr = BookletOCR(lang='en')
results = ocr.process_image(img_np)

# Sort by y-position and filter y<100
title_area = [r for r in results if 60 < r.get('y_position', 0) < 100]
title_area.sort(key=lambda x: x['y_position'])

print("Title area items (y < 100):")
for r in title_area:
    text = r.get('text', '')
    y = r.get('y_position', 0)
    w = r.get('bbox', (0,0,0,0))[2]
    print(f"y={y} w={w:6} | {text}")

print()
print("Issues with current logic:")
print("   1. Only picks ONE highest font_size item")
print("   2. Should merge multiple items from same y but different x (multi-column layout)")
print("   3. 'THEART', 'OF', 'FUGU' should become 'THE ART OF FUGUE'")
