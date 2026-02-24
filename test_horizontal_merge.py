"""Test script for horizontal gap detection"""

import sys
sys.path.insert(0, 'src')

from ocr_processor import BookletOCR
from image_utils import load_image
from markdown_generator import ObsidianMarkdownGenerator

# Simulate _group_single_layout data
test_line = [
    {"text": "THEART", "y_position": 84, "bbox": (110, 81, 506, 70)},
    {"text": "OF", "y_position": 86, "bbox": (663, 86, 136, 70)},
    {"text": "FUGUE", "y_position": 87, "bbox": (882, 87, 311, 70)},
]

print("Test horizontal gap correction:")
print(f"  Input items: {len(test_line)}")

avg_width = sum(t["bbox"][2] for t in test_line) / len(test_line)
max_gap = max((t["bbox"][0] + t["bbox"][2] for t in test_line[1:3]) - 
                 (t["bbox"][0] for t in test_line[1:3]))

print(f"  Average width: {avg_width:.1f}")
print(f"  Max gap: {max_gap} ({max_gap/avg_width*100:.0f}% of avg)")

if max_gap > avg_width * 0.5:
    print(f"  Gap >50% avg width - IMPROPER MERGE NEEDED")
    # Would need to split at gap index 1
    gap_idx = 1
    left = test_line[:gap_idx+1]
    right = test_line[gap_idx+1:]
    print(f"  Left part: {left}")
    print(f"  Right part: {right}")
print(f"  Should be split at gap between '{left[-1]['text']}' and '{right[0]['text']}'")
else:
    print("  Gap OK, single line")
    combined = " ".join(t["text"] for t in test_line)
    print(f"  Combined: {combined}")
