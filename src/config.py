"""Configuration for Booklet OCR

This configuration file controls OCR processing, style detection thresholds,
and output formatting options for the CD Booklet OCR system.
"""

# =============================================================================
# LOGGING SETTINGS
# =============================================================================

LOG_LEVEL = "INFO"

LOG_FILE = None

LOG_TO_CONSOLE = True

LOG_USE_COLORS = True

# =============================================================================
# OCR ENGINE SETTINGS
# =============================================================================

OCR_LANGUAGE = "ch"  # Language for OCR recognition
# Options: 'ch' (Chinese), 'en' (English), 'chinese', 'english'
# Uses Tesseract language mapping: 'ch' → 'chi_sim+eng', 'en' → 'eng'

OCR_USE_GPU = False  # Enable GPU acceleration (if available)
# Note: Requires CUDA-compatible GPU and proper Tesseract GPU build

TESSERACT_CONFIG = "--psm 6 --oem 3"  # Advanced Tesseract configuration
# psm 6  = Assume a single uniform block of text
# oem 3  = Default, based on what is available (LSTM for newer versions)
# Alternative configs:
#   "--psm 3 -l chi_sim+eng"  (Full page OCR with auto page segmentation)
#   "--psm 11 -l chi_sim+eng" (Sparse text with OSD)

# Tesseract executable path (Windows only)
# Set this if Tesseract is not in system PATH
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Layout Analysis Settings
ENABLE_LAYOUT_ANALYSIS = (
    True  # Enable smart layout analysis (multi-page, column detection)
)
LAYOUT_ANALYSIS_METHOD = "contour"  # 'contour' or 'projection'
MIN_TEXT_AREA = 500  # Minimum area in pixels for text region (image filtering)

# Page Detection Settings
PAGE_SPLIT_THRESHOLD = 0.1  # Vertical projection threshold for page splitting
MIN_PAGE_HEIGHT_RATIO = 0.1  # Minimum page height as ratio of image height

# Column Detection Settings
COLUMN_GAP_THRESHOLD = 0.08  # Increased to avoid over-splitting columns in double-page spreads  # Minimum gap width ratio for column separation
MIN_COLUMN_WIDTH_RATIO = 0.1  # Minimum column width ratio
MAX_COLUMNS = 3  # Maximum number of columns to detect

# Text Region Filtering
MIN_TEXT_DENSITY = 0.01  # Minimum text density to keep a region
MAX_TEXT_DENSITY = 0.95  # Maximum text density (filter solid blocks)
MIN_ASPECT_RATIO = 0.05  # Minimum text region aspect ratio (width/height)
MAX_ASPECT_RATIO = 20.0  # Maximum text region aspect ratio (width/height)
MIN_CONTOUR_EXTENT = 0.3  # Minimum contour extent (area/bbox_area)

# =============================================================================
# STYLE DETECTION THRESHOLDS
# =============================================================================

# Heading Detection (based on font size in pixels)
MIN_HEADING_FONT_SIZE = 36

HEADING_SIZE_LEVELS = {
    1: 48,
    2: 42,
    3: 38,
    4: 36,
}

# Bold Text Detection (based on stroke width analysis)
BOLD_STROKE_RATIO = 0.15  # Normalized stroke width threshold
# Range: 0.10-0.20 - Higher = more conservative, fewer false positives
# Calculated as: avg_stroke_width / text_height

BOLD_PIXEL_DENSITY = 0.4  # Pixel density threshold for bold text
# Range: 0.35-0.45 - Higher = detects more bold text
# Calculated as: black_pixels / total_pixels

BOLD_MIN_AREA = 100  # Minimum text region area for bold detection (pixels)
# Prevents false positives on very small text fragments

# Italic Text Detection (based on slant angle analysis)
ITALIC_MIN_ANGLE = 10  # Minimum slant angle (degrees)
ITALIC_MAX_ANGLE = 45  # Maximum slant angle (degrees)
# Range: 10-45 degrees - Outside this range is considered normal text
# Too low (<10): Normal text may be detected as italic
# Too high (>45): Near-vertical text, likely not italic

# =============================================================================
# TEXT GROUPING & LAYOUT ANALYSIS
# =============================================================================

Y_GROUP_THRESHOLD = 30  # Vertical threshold - increased for double-page spreads for line grouping (pixels)
# Text blocks within this Y distance are treated as same line
# Increased from 15 to handle double-page spreads with no page gap

PARAGRAPH_GAP_THRESHOLD = 50  # Increased for better paragraph detection in double-page spreads  # Vertical gap for paragraph separation (pixels)
# Gaps larger than this create new paragraphs
# Adjust for paragraph spacing: wide spacing → higher value (35-40)

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================

OUTPUT_DIR = "output"  # Default output directory for generated markdown files

# Obsidian Frontmatter (YAML metadata)
OBSIDIAN_FRONTMATTER = True  # Include YAML frontmatter at file top
# Contains: created/modified dates, unique ID, tags, etc.

# Obsidian Callouts (colored info boxes)
ENABLE_CALLOUTS = True  # Use Obsidian callout format for page images
# Example: "> [!info]- Page 1 Image\n> ![[page_01.png]]"

PRESERVE_LINE_BREAKS = True  # Preserve explicit line breaks in output
# If False, consecutive text blocks merge into single paragraph

CLEAN_OCR_ARTIFACTS = True  # Remove OCR noise (double lines, special chars)
# Removes: ||||||, =====, random isolated symbols like ©®™

# Page Organization
ENABLE_PAGE_BREAKS = True  # Add markers between processed pages
DETECT_CHAPTERS = True  # Auto-detect chapter headings for organization
CHAPTER_HEADING_LEVELS = [1, 2]  # Markdown heading levels treated as chapters  # Markdown heading levels treated as chapters

# Markdown Formatting
IMPROVE_READABILITY = True  # Add spacing and structure for readability
# - Extra blank lines between paragraphs
# - Consistent list formatting
# - Heading hierarchy maintained

# =============================================================================
# IMAGE PROCESSING
# =============================================================================

# Automatically convert images to RGB
FORCE_RGB_CONVERSION = True  # Always convert to RGB (supports CMYK, grayscale)
# Ensures consistent processing across different scan formats

# Image quality for display purposes
MAX_IMAGE_WIDTH = None  # None = original size, or integer value in pixels
# Example: 1200 limits display width to 1200px (doesn't affect OCR)

# =============================================================================
# ADVANCED OPTIONS
# =============================================================================

# Debug mode (development use only)
DEBUG_MODE = False  # Print detailed processing information
# - Shows each image processing step
# - Outputs detailed style classification
# - Useful for tuning detection thresholds

# Performance options
ENABLE_PARALLEL_PROCESSING = False  # Process multiple images simultaneously
# Requires: sufficient RAM and CPU cores
# Benefit: Faster processing for large booklets

# Confidence filtering
MIN_CONFIDENCE_THRESHOLD = 0.0  # Minimum OCR confidence to include text
# Range: 0.0-1.0 - 0.0 = all text, higher = filter low-confidence text
# Typical values: 0.3-0.5 for cleaner output with some accuracy loss

# =============================================================================
# HYBRID OCR MODE (PDF + Images)
# =============================================================================

USE_HYBRID_OCR = False  # Enable hybrid OCR for PDF+image mixed inputs
# When True: Uses PyMuPDF4LLM for PDFs, Tesseract for images
# Requires: pip install pymupdf4llm

PRIORITY_PDF_TEXT_LAYER = True  # Prefer existing PDF text layer over OCR
# If PDF has embedded text: extract directly (faster, more accurate)
# If False: Always perform OCR on PDF pages

# =============================================================================
# CUSTOM TAGS & ATTRIBUTES (Obsidian)
# =============================================================================

DEFAULT_TAGS = ["ocr", "booklet", "cd-doc", "music"]  # Auto-added tags
# Can customize based on your use case

DOCUMENT_TYPE = "booklet"  # Document type for frontmatter
# Options: 'booklet', 'brochure', 'manual', 'flyer', 'leaflet'

# Show source image in output
EMBED_SOURCE_IMAGES = True  # Include image links in markdown
# Format: ![[relative/path/image.png]]
