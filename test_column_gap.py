import cv2
import numpy as np
import cv2.gray
from pathlib import Path

img = cv2.imread("testcases/HIPPO_20220124_0004.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Horizontal projection
h_proj = np.sum(binary, axis=1)
max_proj = np.max(h_proj) if np.max(h_proj) > 0 else 1
normalized_h = h_proj / max_proj

print("Horizontal projection (x-position histogram):")
low_density_areas = []
in_low = False
start_x = 0
for x in range(len(normalized_h)):
    if normalized_h[x] < 0.1:
        if not in_low:
            in_low = True
            start_x = x
    else:
        if in_low:
            in_low = False
            gap_width = x - start_x
            if gap_width > 100 and gap_width < 600:
                low_density_areas.append((start_x, x, gap_width))
                print(f"  Potential column gap at x={start_x}-{x}, width={gap_width}px")

# Find center region
center_start = int(len(normalized_h) * 0.45)
center_end = int(len(normalized_h) * 0.55)
print(f"\nCenter region (x={center_start}-{center_end}):")
for x in range(center_start, center_end, 20):
    val = normalized_h[x]
    status = "< 0.1" if val < 0.1 else "HIGH" if val > 0.3 else "MED"
    print(f"  x={x}: {status}")
