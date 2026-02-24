# Booklet OCR

Convert CD booklet images from PDF screenshots to Obsidian-compatible Markdown with layout-aware OCR.

## Features

- 📄 **Multi-layout Support**: Handles single-page, double-page spreads, multi-column text
- 🔍 **Multiple OCR Engines**: Support for Tesseract, RapidOCR, EasyOCR, PaddleOCR
- 📝 **Smart Formatting**: Automatic heading detection, list formatting, paragraph grouping
- 🎯 **Style Preservation**: Bold, italic, centered text, headings
- 🔖 **Obsidian Ready**: Frontmatter metadata, callouts, linked images
- 🌍 **Multilingual**: Support for Chinese, English, and 80+ languages

## Quick Start

### Installation

```bash
# Recommended: Use RapidOCR for PDF/Booklets
pip install rapidocr-onnxruntime opencv-python pillow natsort

# Or use EasyOCR
pip install easyocr opencv-python pillow natsort

# Or use PaddleOCR (best for Chinese)
pip install paddleocr opencv-python pillow natsort
```

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for detailed installation instructions.

### Basic Usage

```bash
# Process images in a directory
python src/main.py testcases -o output

# Use different OCR engine
python src/main.py testcases -o output --ocr-backend rapidocr

# Specify language
python src/main.py testcases -o output --lang ch
```

## OCR Engine Comparison

| Engine    | Speed | Accuracy | CPU Usage | Best For |
|-----------|-------|----------|-----------|----------|
| RapidOCR  | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | PDF/Booklets (Recommended) |
| EasyOCR   | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Multilingual text |
| PaddleOCR | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Chinese text |
| Tesseract| ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Maximum compatibility |

## Multiple Environments with UV

If you want to test different OCR engines in isolated environments:

```bash
# Install UV
pip install uv

# Create isolated environment for RapidOCR
uv venv --python 3.10 -o .venv-rapidocr
.venv-rapidocr/Scripts/activate  # Windows
pip install rapidocr-onnxruntime opencv-python pillow natsort

# Create separate environment for EasyOCR
uv venv --python 3.10 -o .venv-easyocr
.venv-easyocr/Scripts/activate
pip install easyocr opencv-python pillow natsort
```

See [docs/OCR_ENGINES.md](docs/OCR_ENGINES.md) for complete OCR engine documentation.

## Configuration

Edit `src/config.py` to customize:

```python
# OCR Settings
OCR_LANGUAGE = "en"  # or "ch" for Chinese
OCR_BACKEND = "rapidocr"  # "tesseract", "rapidocr", "easyocr", "paddleocr"

# Layout Analysis
ENABLE_LAYOUT_ANALYSIS = True
Y_GROUP_THRESHOLD = 30  # Pixels for line grouping

# Output Settings
OBSIDIAN_FRONTMATTER = True
EMBED_SOURCE_IMAGES = True
IMPROVE_READABILITY = True
```

## Output Example

```markdown
---
created: 2024-02-24T00:00:00Z
id: booklet_abc123
tags: [ocr, booklet, cd-doc]
---

# The Art of Fugue

1 Contrapunctus 1 {3:10}
2 Contrapunctus 2 {2:27}
3 Contrapunctus 3 {2:56}
```

## Development

### Running Tests

```bash
python run_tests.py
```

### Code Structure

```
booklet-OCR/
├── src/
│   ├── main.py              # Main CLI
│   ├── ocr_processor.py     # Tesseract OCR
│   ├── ocr_backends.py      # Multi-engine support
│   ├── layout_analyzer.py   # Layout detection
│   ├── markdown_generator.py # Markdown output
│   └── config.py            # Configuration
├── tests/
│   ├── test_*.py           # Unit tests
└── testcases/              # Sample images
```

## Troubleshooting

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for installation issues and [docs/OCR_ENGINES.md](docs/OCR_ENGINES.md) for OCR engine-specific problems.

## Roadmap

- [x] Multiple OCR engine support
- [x] Layout-aware text grouping
- [x] Style preservation (bold, italic, headings)
- [ ] ML-based page boundary detection for double-page spreads
- [ ] Language auto-detection
- [ ] Output to other formats (DOCX, TXT)

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please read CONTRIBUTING.md before submitting PRs.
