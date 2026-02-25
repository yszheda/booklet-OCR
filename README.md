# Booklet OCR

Convert CD booklet images from PDF screenshots to Obsidian-compatible Markdown with layout-aware OCR.

## Features

- 📄 **Multi-layout Support**: Handles single-page, double-page spreads, multi-column text
- 🔍 **Multiple OCR Engines**: Support for Tesseract, RapidOCR, EasyOCR, PaddleOCR
- 📝 **Smart Formatting**: Automatic heading detection, list formatting, paragraph grouping
- 🎯 **Style Preservation**: Bold, italic, centered text, headings
- 🔖 **Obsidian Ready**: Clean markdown output (no Obsidian-specific features by default)
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
python src/main.py data/testcases -o output

# Compare output with reference
diff -u data/references/references.md output/testcases.md
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
OBSIDIAN_FRONTMATTER = False  # Disabled for clean output
EMBED_SOURCE_IMAGES = False  # Disabled for clean output
IMPROVE_READABILITY = False  # Disabled for clean output
```

## Output Example

```markdown
#### THE ART OF FUGUE is Bach's final major instrumental composition and a farewell testament for the ages. It is an ordered set of fourteen fugues and four canons, all deriving from a single theme, and all sharing the same key of D minor.

To see The Art of Fugue clearly for what it is, a description of the other above-mentioned monuments will help us.
```

## Development

### Code Structure

```
booklet-OCR/
├── src/
│   ├── main.py              # Main CLI entry point
│   ├── rapidocr_processor.py # RapidOCR engine integration
│   ├── markdown_generator.py  # Markdown output generator
│   ├── layout_analyzer.py    # Layout detection
│   ├── config.py             # Configuration settings
│   ├── image_utils.py        # Image I/O utilities
│   ├── logger.py             # Logging setup
│   ├── hybrid_ocr.py         # Multi-engine support
│   └── ocr_processor.py      # Tesseract OCR (legacy)
├── data/
│   ├── testcases/           # Test image input
│   └── references/          # Expected output references
├── tests/                   # Unit tests
├── tools/                   # Utility scripts
├── docs/                    # Documentation
├── output/                  # Generated output (gitignored)
└── requirements.txt         # Python dependencies
```

## Current Development Status (Feb 2026)

### What's Working:
- Clean markdown output (no Obsidian features)
- Timestamp bracket normalization: {3:10} format
- Paragraph merging (text flows as continuous paragraphs)
- Title and centered text formatting with ♪ symbols
- Hyphen repair for line breaks

### Known Limitations:
- Track listings from multi-column pages may be merged (column detection disabled)
- Some word spacing issues (e.g., "counterpointare", "themewhich") - requires NLP
- Missing markdown emphasis (*italics*) for titles
- Some headings use #### instead of ### due to conservative detection

### Quick Test:
```bash
python src/main.py data/testcases -o output
# Compare output with reference
diff -u data/references/references.md output/testcases.md
```

### Python Environment:
```bash
# Using uv for isolated environment (optional):
pip install uv
uv venv --python 3.10 -o .venv-ocr
# Windows:
# .venv-ocr/Scripts/activate
# pip install rapidocr-onnxruntime opencv-python pillow natsort
```

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please read CONTRIBUTING.md before submitting PRs.
