"""Unit tests for logger module"""

import unittest
import sys
import logging
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from logger import setup_logging, get_logger, info, error, warning, debug, _loggers


class TestLogger(unittest.TestCase):
    """Test logging utilities"""

    def setUp(self):
        """Reset logging before each test"""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        _loggers.clear()

    def test_setup_logging(self):
        """Test logging setup"""
        setup_logging(log_level="INFO", log_to_console=True)
        self.assertIsNotNone(get_logger("test"))

    def test_get_logger(self):
        """Test getting logger instance"""
        setup_logging(log_level="INFO", log_to_console=False)
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")

        # Should return same logger instance
        self.assertIs(logger1, logger2)

    def test_get_logger_different_names(self):
        """Test getting loggers with different names"""
        setup_logging(log_level="INFO", log_to_console=False)
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        # Should return different logger instances
        self.assertIsNot(logger1, logger2)

    def test_log_levels(self):
        """Test different log levels"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            log_file = f.name

        try:
            setup_logging(log_level="DEBUG", log_file=log_file, log_to_console=False)
            logger = get_logger("test")

            # These should not raise exceptions
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

            # Check log file was created and has content
            with open(log_file, "r") as f:
                content = f.read()
                self.assertIn("Info message", content)
        finally:
            root_logger = logging.getLogger(); root_logger.handlers.clear(); Path(log_file).unlink(missing_ok=True)

    def test_log_filter_by_level(self):
        """Test that log level filtering works"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            log_file = f.name

        try:
            setup_logging(log_level="WARNING", log_file=log_file, log_to_console=False)
            logger = get_logger("test")

            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

            with open(log_file, "r") as f:
                content = f.read()
                # DEBUG and INFO should not appear
                self.assertNotIn("Debug message", content)
                self.assertNotIn("Info message", content)
                # WARNING and ERROR should appear
                self.assertIn("Warning message", content)
                self.assertIn("Error message", content)
        finally:
            root_logger = logging.getLogger(); root_logger.handlers.clear(); Path(log_file).unlink(missing_ok=True)

    def test_convenience_functions(self):
        """Test convenience logging functions"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            log_file = f.name

        try:
            setup_logging(log_level="INFO", log_file=log_file, log_to_console=False)

            # These should not raise exceptions
            info("Info message")
            warning("Warning message")
            error("Error message")
            debug("Debug message")
        finally:
            root_logger = logging.getLogger(); root_logger.handlers.clear(); Path(log_file).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
