import cv2
import numpy as np
import pytesseract
import re
import argparse
from PIL import Image
from googletrans import Translator
import os
import matplotlib.pyplot as plt
from matplotlib import patches

# Check if Tesseract is installed and set path for Windows
try:
    pytesseract.get_tesseract_version()
except:
    # Set the path to the Tesseract executable (modify as needed)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize translator
translator = Translator()

def detect_columns(image, min_area=1000, min_width=50, min_height=100):
    """
    Detect columns in the image using contour detection
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
        
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size
    columns = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w * h > min_area and w > min_width and h > min_height:
            columns.append((x, y, w, h))
    
    # Sort columns from left to right
    columns.sort(key=lambda x: x[0])
    
    # Merge overlapping columns
    i = 0
    while i < len(columns) - 1:
        x1, y1, w1, h1 = columns[i]
        x2, y2, w2, h2 = columns[i + 1]
        
        # Check if columns overlap horizontally
        if x1 + w1 >= x2:
            # Merge columns
            new_x = min(x1, x2)
            new_y = min(y1, y2)
            new_w = max(x1 + w1, x2 + w2) - new_x
            new_h = max(y1 + h1, y2 + h2) - new_y
            columns[i] = (new_x, new_y, new_w, new_h)
            columns.pop(i + 1)
        else:
            i += 1
    
    return columns

def visualize_columns(image, columns):
    """
    Visualize detected columns for debugging
    """
    fig, ax = plt.subplots(1)
    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    for column in columns:
        x, y, w, h = column
        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
    
    plt.show()

def process_image(image_path, target_language='en', visualize=False):
    """
    Process the image: detect columns, perform OCR, and translate text
    """
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at {image_path}")
    
    # Detect columns
    columns = detect_columns(image)
    
    if visualize:
        visualize_columns(image, columns)
    
    # If no columns detected, process the entire image
    if not columns:
        columns = [(0, 0, image.shape[1], image.shape[0])]
    
    results = []
    for i, (x, y, w, h) in enumerate(columns):
        # Extract column region
        column_img = image[y:y+h, x:x+w]
        
        # Determine the language to use for OCR
        # Try with multiple languages for better accuracy
        text = pytesseract.image_to_string(column_img, lang='eng+deu+fra+ita+chi_sim+jpn')
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        if not text:
            continue
            
        # Detect language
        try:
            detected_lang = translator.detect(text).lang
            print(f"Column {i+1} detected language: {detected_lang}")
        except:
            detected_lang = 'en'  # Default to English if detection fails
        
        # Translate if needed and target language is different from detected
        translated_text = text
        if target_language != detected_lang:
            try:
                translated_text = translator.translate(text, dest=target_language).text
                print(f"Translated column {i+1} from {detected_lang} to {target_language}")
            except Exception as e:
                print(f"Translation error: {e}")
        
        results.append({
            'column': i+1,
            'original_text': text,
            'detected_language': detected_lang,
            'translated_text': translated_text
        })
    
    return results

def save_as_markdown(results, output_path):
    """
    Save the OCR results as a markdown file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# OCR and Translation Results\n\n")
        
        for result in results:
            f.write(f"## Column {result['column']}\n\n")
            f.write("### Original Text\n\n")
            f.write(f"```\n{result['original_text']}\n```\n\n")
            f.write(f"*Detected language: {result['detected_language']}*\n\n")
            
            if result['original_text'] != result['translated_text']:
                f.write("### Translated Text\n\n")
                f.write(f"```\n{result['translated_text']}\n```\n\n")
            
            f.write("---\n\n")

def save_as_html(results, output_path):
    """
    Save the OCR results as an HTML file
    """
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OCR and Translation Results</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
        .column { margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        .original, .translated { background-color: #f9f9f9; padding: 15px; border-radius: 5px; white-space: pre-wrap; }
        h1 { color: #333; }
        h2 { color: #444; }
        h3 { color: #666; }
        .language { font-style: italic; color: #777; margin-bottom: 15px; }
    </style>
</head>
<body>
    <h1>OCR and Translation Results</h1>
"""
    
    for result in results:
        html += f"""    <div class="column">
        <h2>Column {result['column']}</h2>
        <h3>Original Text</h3>
        <div class="language">Detected language: {result['detected_language']}</div>
        <div class="original">{result['original_text']}</div>
"""
        
        if result['original_text'] != result['translated_text']:
            html += f"""        <h3>Translated Text</h3>
        <div class="translated">{result['translated_text']}</div>
"""
        
        html += "    </div>\n"
    
    html += "</body>\n</html>"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    parser = argparse.ArgumentParser(description='OCR and translation tool for multi-language documents')
    parser.add_argument('image_path', help='Path to the input image')
    parser.add_argument('--target_lang', default='en', help='Target language for translation (default: en)')
    parser.add_argument('--output_format', choices=['markdown', 'html', 'both'], default='both', 
                        help='Output format (default: both)')
    parser.add_argument('--visualize', action='store_true', help='Visualize detected columns')
    args = parser.parse_args()
    
    # Process the image
    results = process_image(args.image_path, args.target_lang, args.visualize)
    
    # Create output directory if it doesn't exist
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results
    base_name = os.path.splitext(os.path.basename(args.image_path))[0]
    
    if args.output_format in ['markdown', 'both']:
        md_path = os.path.join(output_dir, f"{base_name}_ocr.md")
        save_as_markdown(results, md_path)
        print(f"Markdown output saved to {md_path}")
    
    if args.output_format in ['html', 'both']:
        html_path = os.path.join(output_dir, f"{base_name}_ocr.html")
        save_as_html(results, html_path)
        print(f"HTML output saved to {html_path}")

if __name__ == "__main__":
    main()