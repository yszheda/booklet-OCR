"""Test title fixes"""

import sys
sys.path.insert(0, ".")

# Test merging
parts = ["THEART", "OF", "FUGUE", "THEA", "RT", "OF", "FUGUE"]

# Calculate widths
widths = [len(t) * 8 for t in parts]
avg_width = sum(widths) / len(widths)

max_gap = 0
for i in range(len(parts)-1):
    gap = (i+1)*8 - sum(widths[:i+1])
    if gap > max_gap:
        max_gap = gap

print(f"Parts: {parts}")
print(f"Widths: {widths}")
print(f"Avg width: {avg_width:.0f}")
print(f"Max gap: {max_gap}")
print(f"Gap ratio: {max_gap/avg_width*100:.1f}%")

if max_gap > avg_width * 0.4:
    split_idx = widths.index(max_gap)
    result = " ".join(parts[:split_idx+1]) + "   " + " ".join(parts[split_idx+1:])
    print(f"Split at index {split_idx}: {result}")
else:
    result = " ".join(parts)
    print(f"No split needed: {result}")
