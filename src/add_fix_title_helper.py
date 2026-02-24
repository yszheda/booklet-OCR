"""Helper functions to fix broken OCR titles"""

import re

def merge_horizontal_title_parts(texts, max_gap_ratio=0.5):
    """
    Merge title text fragments that were mistakenly split across columns.
    texts: list of text strings
    max_gap_ratio: if gap > (max_width * max_ratio), split instead
    """
    if len(texts) <= 1:
        return texts[0]
    
    # Calculate widths
    widths = []
    for text in texts:
        # Approximate character width (average char = 8)
        approx_width = len(text) * 8
        widths.append(approx_width)
    
    if not widths:
        return texts[0]
    
    avg_width = sum(widths) / len(widths)
    max_gap = max((widths[i+1] - widths[i] if i+1 < len(widths) else 0 for i in range(len(widths)-1))
    
    # If max gap > 50% of avg, split
    if max_gap > avg_width * 0.5:
        split_idx = widths.index(max_gap)
        left_part = " ".join(texts[:split_idx+1])
        right_part = " ".join(texts[split_idx+1:])
        return f"{left_part}   {right_part}"
    else:
        return " ".join(texts)


def fix_broken_title(title_text: str) -> str:
    """Fix commonly broken OCR titles"""
    if not title_text or len(title_text) < 5:
        return title_text
    
    # Known OCR errors
    # "EHREART" -> "THE ART"
    # "EARTHAR" -> "THE ART"  
    # "EHREART OF" -> "THE ART OF" (remove "OF")
    
    if "EHREART OF" in title_text.upper():
        title_text = "THE ART OF" + title_text.split("OF")[-1:]
    
    elif "EARTHAR" in title_text.upper():
        title_text = "THE ART" + title_text.split("AR")[-1:]
    
    elif "EARTHAR TOF" in title_text.upper():
        title_text = "THE ART OF" + title_text.split("TOF")[-1:]
    
    return title_text.title()


if __name__ == "__main__":
    print("Test title fixes:")
    
    # Test 1
    broken = "EHREART OF FUGU"
    fixed = fix_broken_title(broken)
    print(f"  '{broken}' -> '{fixed}'")
    
    # Test 2
    broken2 = "EARTHAR TOF UGE"  
    fixed2 = fix_broken_title(broken2)
    print(f"  '{broken2}' -> '{fixed2}'")
    
    # Test 3
    parts = ["THEART", "OF", "FUGUE"]
    merged = merge_horizontal_title_parts(parts)
    print(f"  {parts} -> {merged}")
    
    # Test 4  
    parts2 = ["THE", "ART", "OF", "FUGE"]
    merged2 = merge_horizontal_title_parts(parts2)
    print(f"  {parts2} -> {merged2}")
    
    # Test 5
    parts3 = ["THE", "OF", "FUGUE", "THEA", "RT", "OF", "FUGUE"]
    merged3 = merge_horizontal_title_parts(parts3)
    print(f"  {parts3} -> {merged3}")
