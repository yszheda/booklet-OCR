# Installation Guide

## Requirements

- Python 3.8 or higher
- UV (recommended for environment isolation)

## Quick Start

### Option 1: Using UV (Recommended)

```bash
# Install UV
pip install uv

# Create isolated environment
uv venv

# Activate environment (Windows)
.venv\Scripts\activate

# Activate environment (Linux/Mac)
source .venv/bin/activate

# Install with RapidOCR (recommended for PDF/Booklets)
pip install rapidocr-onnxruntime opencv-python pillow natsort

# Install with EasyOCR
pip install easyocr opencv-python pillow natsort

# Install with PaddleOCR
pip install paddleocr opencv-python pillow natsort
```

### Option 2: Using pip directly

```bash
# Install with RapidOCR
pip install rapidocr-onnxruntime opencv-python pillow natsort

# Install with EasyOCR
pip install easyocr opencv-python pillow natsort

# Install with PaddleOCR
pip install paddleocr opencv-python pillow natsort
```

## Tesseract Setup (Optional)

If you prefer using Tesseract:

### Windows
1. Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Extract to a directory (e.g., `C:\Program Files\Tesseract-OCR`)
3. Add to PATH or set `TESSERACT_PATH` in `src/config.py`

### Linux
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr libtesseract-dev

# Fedora
sudo dnf install tesseract

# Arch
sudo pacman -S tesseract
```

### macOS
```bash
brew install tesseract
```

## Verifying Installation

```bash
# Test OCR backends
python -c "from src.ocr_backends import create_ocr_backend; engine = create_ocr_backend('rapidocr'); print('✓ RapidOCR ready')"

# Run tests
python run_tests.py

# Process sample images
python src/main.py testcases -o output
```

## Troubleshooting

### RapidOCR not installing
```bash
# Try installing ONNX Runtime first
pip install onnxruntime-gpu  # For GPU
pip install onnxruntime     # For CPU
pip install rapidocr-onnxruntime
```

### PaddleOCR memory issues
```bash
# Limit CPU cores used
export OMP_NUM_THREADS=2
python src/main.py testcases -o output
```

### EasyOCR downloading models
EasyOCR will download models on first use (~100MB). Ensure stable internet connection.

## Environment Variables

```bash
# Set OCR backend
export OCR_BACKEND=rapidocr

# Set language
export OCR_LANGUAGE=en

# For Tesseract: set path
export TESSERACT_PATH=/path/to/tesseract
```

## Supported OCR Engines

| Engine    | Install Command                          | Languages | Speed  | Accuracy |
|-----------|------------------------------------------|-----------|--------|----------|
| RapidOCR  | `pip install rapidocr-onnxruntime`       | 80+       | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| EasyOCR   | `pip install easyocr`                     | 80+       | ⭐⭐⭐   | ⭐⭐⭐⭐ |
| PaddleOCR | `pip install paddleocr`                    | 80+       | ⭐⭐⭐   | ⭐⭐⭐⭐⭐ |
| Tesseract| `pip install pytesseract` + binary        | 125+      | ⭐⭐⭐   | ⭐⭐⭐   |

## Development Installation

```bash
# Clone repository
git clone https://github.com/yszheda/booklet-OCR.git
cd booklet-OCR

# Install dev dependencies
pip install black pytest flake8

# Run tests
python run_tests.py

# Format code
black src/ tests/
```
