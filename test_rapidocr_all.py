import cv2
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, "src")
from image_utils import get_image_files, load_image
from ocr_backends import create_ocr_backend
from layout_analyzer import LayoutAnalyzer
from markdown_generator import ObsidianGenerator
import config

test_images = get_image_files("testcases")
print(f"Processing {len(test_images)} images with RapidOCR\n")

engine = create_ocr_backend(backend="rapidocr", lang="en")
analyzer = LayoutAnalyzer()
generator = ObsidianMarkdownGenerator()

class SimpleOCR:
    def classify_text_style(self, text_info):
        return {
            "is_heading": text_info.get("font_size", 0) >= 36,
            "is_bold": False,
            "is_italic": False,
            "is_centered": False,
            "is_list": False,
        }
    
    def group_text_lines(self, texts, y_threshold=30):
        if not texts:
            return []
        texts = sorted(texts, key=lambda x: (x["y_position"], x["bbox"][0]))
        grouped = []
        current_line = [texts[0]]
        current_y = texts[0]["y_position"]
        
        for text in texts[1:]:
            y_diff = abs(text["y_position"] - current_y)
            if y_diff <= y_threshold:
                current_line.append(text)
            else:
                grouped.append(self._merge_line(current_line))
                current_line = [text]
                current_y = text["y_position"]
        
        if current_line:
            grouped.append(self._merge_line(current_line))
        return grouped
    
    def _merge_line(self, line_texts):
        if len(line_texts) == 1:
            return line_texts[0]
        sorted_texts = sorted(line_texts, key=lambda x: x["bbox"][0])
        combined_text = " ".join(t["text"] for t in sorted_texts)
        return {"text": combined_text, **line_texts[0]}

ocr = SimpleOCR()

images_data = []
for img_file in test_images:
    print(f"[{img_file.name}]")
    img_pil = load_image(img_file)
    img_np = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    results = engine.process_image(img_np)
    print(f"  Detected {len(results)} items")
    
    for r in results:
        r["styles"] = ocr.classify_text_style(r)
        r["layout_info"] = {"page_index": 1, "column_index": 1}
    
    grouped = ocr.group_text_lines(results, y_threshold=30)
    print(f"  Merged to {len(grouped)} lines")
    
    images_data.append({
        "image_path": str(img_file),
        "results": grouped,
        "num_texts": len(grouped),
    })

output_path = "output_rapidocr/testcases.md"
Path(output_path).parent.mkdir(parents=True, exist_ok=True)
generator.generate(images_data, output_path, "testcases")

# Fix artifacts
print("\n=== Fixing OCR artifacts ===")
exec(open('fix_ocr_artifacts.py').read())

print(f"\nDone! Output: {output_path}")
