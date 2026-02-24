"""Image loading and sorting utilities"""

import os
from pathlib import Path
from PIL import Image
from natsort import natsorted
from logger import get_logger

logger = get_logger(__name__)


def get_image_files(directory):
    """
    Get all image files from the directory in natural order
    """
    supported_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}

    image_files = []
    for file in Path(directory).iterdir():
        if file.suffix.lower() in supported_extensions and file.is_file():
            image_files.append(file)

    # Natural sort (1, 2, 10 instead of 1, 10, 2)
    return natsorted(image_files)


def load_image(image_path):
    """
    Load an image file and return as PIL Image
    """
    try:
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image
    except Exception as e:
        logger.error(f"Error loading {image_path}: {e}")
        return None


def validate_directory(directory):
    """
    Validate that the directory exists and contains images
    """
    path = Path(directory)

    if not path.exists():
        raise ValueError(f"Directory not found: {directory}")

    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    images = get_image_files(directory)
    if not images:
        raise ValueError(f"No images found in: {directory}")

    return len(images)
