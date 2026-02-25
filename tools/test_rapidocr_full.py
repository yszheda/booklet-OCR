#!/usr/bin/env python
import cv2
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.ocr_backends import create_ocr_backend
from image_utils import get_image_files, load_image
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
    img = load_image(img_file)
    if img is None:
        continue
    
    print(f"[{img_file.name}] Processing...")
    img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    results = engine.process_image(img_np)
    print(f"  Detected {len(results)} text items")
    
    layout_results = results
    if config.ENABLE_LAYOUT_ANALYSIS:
        layout = analyzer.analyze_layout(img_np[:, :, 0])
        for text_info in layout_results:
            text_info["layout_info"] = analyzer.get_layout_annotation(text_info, layout)
    
    grouped = engine.group_text_lines if hasattr(engine, 'group_text_lines') else (lambda x: x)
    layout_results = grouped(layout_results)
    
    for text_info in layout_results:
        text_info["styles"] = engine.classify_text_style(text_info) if hasattr(engine, 'classify_text_style') else {}
    
    images_data.append({
        "image_path": str(img_file),
        "results": layout_results,
        "num_texts": len(layout_results),
    })

output_path = "output_rapidocr/testcases.md"
Path(output_path).parent.mkdir(exist_ok=True)
generator.generate(images_data, output_path, "testcases")
print(f"\nSaved to: {output_path}")
