"""Test horizontal merging logic"""
# Test data
test_line = [
    {"text": "THEART", "y_position": 84, "bbox": (110, 81, 506, 70)},
    {"text": "OF", "y_position": 86, "bbox": (663, 86, 136, 70)},
    {"text": "FUGUE", "y_position": 87, "bbox": (882, 87, 311, 70)},
]

x_coords = [t["bbox"][0] for t in test_line]
x_ends = [t["bbox"][0] + t["bbox"][2] for t in test_line]

print("X coordinates:", x_coords)
print("X end coordinates:", x_ends)
print("Gaps:", [x_ends[i] - x_ends[i-1] for i in range(1, len(x_ends))])

avg_width = sum(t["bbox"][2] for t in test_line) / len(test_line)
max_gap = max((x_ends[i] - x_ends[i-1] for i in range(1, len(x_ends)) - 1))

print(f"\nAvg width: {avg_width:.0f}")
print(f"Max gap: {max_gap}")
print(f"Gap percent: {max_gap/avg_width*100:.0f}%")

if max_gap > avg_width * 0.4:
    print("SHOULD NOT MERGE - gap too large!")
else:
    print("Merge OK")
