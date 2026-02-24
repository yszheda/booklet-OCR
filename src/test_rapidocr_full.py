import cv2
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

sys.path.insert(0, "src")
from image_utils import get_image_files, load_image

from ocr_backends import create_ocr_backend
import config

test_images = get_image_files("testcases")
print(f"Processing {len(test_images)} image(s) with RapidOCR\n")

engine = create_ocr_backend(backend="rapidocr", lang="en")

from layout_analyzer import LayoutAnalyzer
from markdown_generator import ObsidianMarkdownGenerator
import numpy as np

analyzer = LayoutAnalyzer()
generator = ObsidianMarkdownGenerator()

images_data = []
for img_file in test_images[:5]:
    print(f"[{img_file.name}] Processing...")
    img_pil = load_image(img_file)
    if img_pil is None:
        continue
    
    img_np = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    results = engine.process_image(img_np)
    print(f"  Detected {len(results)} text items")
    
    # Simple layout annotation
    layout = analyzer.analyze_layout(cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY))
    for text_info in results:
        text_info["layout_info"] = analyzer.get_layout_annotation(text_info, layout)
    
    # Style classification
    for text_info in results:
        styles = {
            "is_heading": text_info.get("font_size", 0) >= 36,
            "is_bold": False,
            "is_italic": False,
            "is_centered": False,
        }
        if styles["is_heading"]:
            styles["heading_level"] = 4 if text_info["font_size"] < 50 else 3
        text_info["styles"] = styles
    
    images_data.append({
        "image_path": str(img_file),
        "results": results,
        "num_texts": len(results),
    })

output_path = "output_rapidocr/testcases.md"
Path(output_path).parent.mkdir(exist_ok=True)
generator.generate(images_data, output_path, "testcases")
print(f"\nSaved to: {output_path}")
