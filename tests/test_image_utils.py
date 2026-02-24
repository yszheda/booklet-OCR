"""Unit tests for image_utils module"""

import unittest
import sys
from pathlib import Path
from PIL import Image

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from image_utils import get_image_files, load_image, validate_directory


class TestImageUtils(unittest.TestCase):
    """Test image utilities"""

    @classmethod
    def setUpClass(cls):
        """Setup test fixtures"""
        cls.test_dir = Path(__file__).parent.parent / "testcases"
        cls.output_dir = Path(__file__).parent / "test_output"
        cls.output_dir.mkdir(exist_ok=True)

    def test_get_image_files(self):
        """Test getting image files from directory"""
        files = get_image_files(self.test_dir)
        self.assertIsInstance(files, list)
        self.assertGreater(len(files), 0)

        # Check all files are images
        for f in files:
            self.assertIn(
                f.suffix.lower(), {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
            )

    def test_get_image_files_natural_sort(self):
        """Test natural sorting of image files"""
        files = get_image_files(self.test_dir)
        # Natural sort should put 10 after 2, not before
        file_names = [f.name for f in files]
        self.assertTrue(self.is_naturally_sorted(file_names))

    def is_naturally_sorted(self, names):
        """Helper to check natural sorting"""
        from natsort import natsorted

        return names == natsorted(names)

    def test_load_image(self):
        """Test loading image file"""
        files = get_image_files(self.test_dir)
        if not files:
            return

        image = load_image(files[0])
        self.assertIsNotNone(image)
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.mode, "RGB")

    def test_load_nonexistent_image(self):
        """Test loading non-existent image"""
        image = load_image("nonexistent.jpg")
        self.assertIsNone(image)

    def test_validate_directory_valid(self):
        """Test validating a valid directory with images"""
        num_images = validate_directory(self.test_dir)
        self.assertGreater(num_images, 0)

    def test_validate_directory_nonexistent(self):
        """Test validating non-existent directory"""
        with self.assertRaises(ValueError):
            validate_directory("nonexistent_dir")

    def test_validate_directory_no_images(self):
        """Test validating directory with no images"""
        empty_dir = self.output_dir / "empty"
        empty_dir.mkdir(exist_ok=True)

        with self.assertRaises(ValueError):
            validate_directory(empty_dir)


if __name__ == "__main__":
    unittest.main()
