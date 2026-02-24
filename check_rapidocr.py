# Check RapidOCR availability
try:
    sys.path.insert(0, 'src')
    from ocr_backends import create_ocr_backend
    engine = create_ocr_backend('rapidocr', 'en')
    print("RapidOCR engine available")
except:
    print("RapidOCR NOT installed")
