"""Test runner script for Booklet OCR"""

import unittest
import sys
from pathlib import Path

# Add src and tests to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))


def run_tests(verbose=False):
    """Run all tests"""

    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / "tests"
    suite = loader.discover(str(start_dir), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    success = run_tests(verbose=verbose)

    sys.exit(0 if success else 1)
