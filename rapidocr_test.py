import cv2
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, "src")
from image_utils import get_image_files, load_image
from ocr_backends import create_ocr_backend
from layout_analyzer import LayoutAnalyzer
from markdown_generator import ObsidianMarkdownGenerator
import config

test_images = get_image_files("testcases")
print(f"Processing {len(test_images)} image(s) with RapidOCR\n")

engine = create_ocr_backend(backend="rapidocr", lang="en")
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
    
    for text_info in results[:5]:
        print(f"    - {text_info['text'][:50]}")
    
    # Layout annotation
    layout = analyzer.analyze_layout(cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY))
    for text_info in results:
        text_info["layout_info"] = analyzer.get_layout_annotation(text_info, layout)
    
    # Style classification
    from ocr_processor import BookletOCR
    ocr = BookletOCR(lang="en")
    for text_info in results:
        text_info["styles"] = ocr.classify_text_style(text_info)
    
    # Note: RapidOCR doesn't have group_text_lines yet, so use existing results
    from ocr_processor import BookletOCR
    ocr = BookletOCR(lang="en")
    ocr.layout_analyzer = analyzer
    results = ocr.group_text_lines(results, y_threshold=30)
    
    images_data.append({
        "image_path": str(img_file),
        "results": results,
        "num_texts": len(results),
    })

output_path = "output_rapidocr/testcases.md"
Path(output_path).parent.mkdir(exist_ok=True)
generator.generate(images_data, output_path, "testcases")
print(f"\nSaved to: {output_path}")
