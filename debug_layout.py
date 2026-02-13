"""Debug script to analyze layout detection"""

import cv2
import numpy as np
from PIL import Image
import sys

sys.path.insert(0, "src")

from layout_analyzer import LayoutAnalyzer
from ocr_processor import BookletOCR
import config

image_path = sys.argv[1] if len(sys.argv) > 1 else "test_single/HIPPO_20220124_0006.jpg"

print(f"Analyzing: {image_path}")
print("=" * 60)

# Load image
image = Image.open(image_path)
if image.mode != "RGB":
    image = image.convert("RGB")
image_np = np.array(image)

print(f"Image size: {image_np.shape[1]} x {image_np.shape[0]}")

# Initialize layout analyzer
analyzer = LayoutAnalyzer()

# Detect pages
print("\n--- PAGE DETECTION ---")
pages = analyzer.detect_pages(image_np)
print(f"Detected {len(pages)} page(s)")
for i, page in enumerate(pages):
    print(f"  Page {i + 1}: type={page['type']}, bbox={page['bbox']}")

# For each page, detect columns
for page_idx, page in enumerate(pages):
    print(f"\n--- PAGE {page_idx + 1} COLUMN DETECTION ---")
    x, y, w, h = page["bbox"]
    page_region = image_np[y : y + h, x : x + w]

    columns = analyzer.detect_columns(page_region)
    print(f"Detected {len(columns)} column(s)")
    for col in columns:
        print(f"  Column {col['index']}: bbox={col['bbox']}")

    # Detect image regions
    print(f"\n--- PAGE {page_idx + 1} IMAGE REGION DETECTION ---")
    image_regions = analyzer.detect_image_regions(page_region)
    print(f"Detected {len(image_regions)} image region(s)")
    for ir in image_regions:
        print(
            f"  Image region: bbox={ir['bbox']}, density={ir['density']:.3f}, area={ir['area']}"
        )

# Now test OCR WITHOUT layout analysis first
print("\n" + "=" * 60)
print("OCR PROCESSING WITHOUT LAYOUT ANALYSIS")
print("=" * 60)

config.ENABLE_LAYOUT_ANALYSIS = False
ocr = BookletOCR(lang="en", use_gpu=False)

results_no_layout = ocr.process_image(image_np)
print(f"\nTotal text blocks (no layout): {len(results_no_layout)}")
for r in results_no_layout[:10]:
    print(f"  - '{r['text'][:40]}' @ y={r['y_position']:.0f}")

# Now test with layout analysis
print("\n" + "=" * 60)
print("OCR PROCESSING WITH LAYOUT ANALYSIS")
print("=" * 60)

config.ENABLE_LAYOUT_ANALYSIS = True
ocr2 = BookletOCR(lang="en", use_gpu=False)

results = ocr2.process_image(image_np)
print(f"\nTotal text blocks (with layout): {len(results)}")

# Group by page and column
from collections import defaultdict

grouped = defaultdict(list)
for r in results:
    layout = r.get("layout_info", {})
    key = (layout.get("page_index", 1), layout.get("column_index", 1))
    grouped[key].append(r)

print("\nText blocks by (page, column):")
for key in sorted(grouped.keys()):
    page_idx, col_idx = key
    texts = grouped[key]
    print(f"\n  Page {page_idx}, Column {col_idx}: {len(texts)} blocks")
    for t in texts[:3]:
        print(f"    - '{t['text'][:50]}...' @ y={t['y_position']:.0f}")
    if len(texts) > 3:
        print(f"    ... and {len(texts) - 3} more")
