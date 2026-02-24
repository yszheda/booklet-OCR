# OCR Backend Options

This project supports multiple OCR backends for optimal performance.

## Supported OCR Engines

### 1. Tesseract (Default)
- **Installation**: `pip install pytesseract`
- **Setup**: Download Tesseract executable from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- **Pros**: Mature, supports 125+ languages
- **Cons**: Slower, less accurate for modern fonts

### 2. RapidOCR (Recommended for PDF/Booklets)
- **Installation**: `pip install rapidocr-onnxruntime`
- **Setup**: No external dependencies
- **Pros**: Fast (CPU optimized), good accuracy for printed text, lightweight
- **Cons**: Limited language support compared to Tesseract

### 3. EasyOCR
- **Installation**: `pip install easyocr`
- **Setup**: No external dependencies
- **Pros**: Deep learning based, supports 80+ languages
- **Cons**: Heavier, slower processing

### 4. PaddleOCR
- **Installation**: `pip install paddleocr`
- **Setup**: No external dependencies
- **Pros**: Best for Chinese text, high accuracy
- **Cons**: Requires more memory, slower

## Installation with UV (Recommended for Isolation)

```bash
# Install UV
pip install uv

# Create isolated environment
uv venv --python 3.10
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install RapidOCR (recommended for PDF/Booklets)
pip install rapidocr-onnxruntime opencv-python pillow natsort

# Or install EasyOCR
pip install easyocr opencv-python pillow natsort

# Or install PaddleOCR
pip install paddleocr opencv-python pillow natsort
```

## Usage

### Using Tesseract (Default)
```bash
python src/main.py testcases -o output
```

### Using RapidOCR
```bash
pip install rapidocr-onnxruntime
python src/main.py testcases -o output --ocr-backend rapidocr
```

### Using EasyOCR
```bash
pip install easyocr
python src/main.py testcases -o output --ocr-backend easyocr
```

## Performance Comparison

| Engine    | Speed  | Accuracy | CPU Usage | Memory | Languages |
|-----------|--------|----------|-----------|--------|-----------|
| Tesseract | ★★★☆☆  | ★★★☆☆   | ★★☆☆☆    | ★★★☆☆  | 125+      |
| RapidOCR  | ★★★★★  | ★★★★☆   | ★★★★☆    | ★★☆☆☆  | 80+       |
| EasyOCR   | ★★☆☆☆  | ★★★★☆   | ★★★☆☆    | ★★★★★  | 80+       |
| PaddleOCR | ★★☆☆☆  | ★★★★★   | ★★★★☆    | ★★★★★  | 80+       |

## Recommendations

- **CD Booklets**: Use **RapidOCR** for best speed/accuracy balance
- **Mixed text**: Use **EasyOCR** for better multilingual support
- **Chinese text**: Use **PaddleOCR** for optimal Chinese recognition
- **Maximum compatibility**: Use **Tesseract** (default)
