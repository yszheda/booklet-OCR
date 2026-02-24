import cv2
from rapidocr_onnxruntime import RapidOCR

test_image = "../testcases/HIPPO_20220124_0004.jpg"
img = cv2.imread(test_image)

ocr = RapidOCR()
result = ocr(img)

print(f"Result type: {type(result)}")
print(f"Result length: {len(result) if result else 0}")

if result:
    print(f"First element type: {type(result[0])}")
    print(f"First result: {result[0][:2] if isinstance(result[0], list) else result[0]}")
    
    if result[0]:
        print(f"\nFirst 5 text items:")
        for i, item in enumerate(result[0][:5], 1):
            print(f"  {i}. {item}")
