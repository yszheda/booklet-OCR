"""Logging configuration for Booklet OCR

Provides centralized logging configuration with support for:
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output
- Structured log format with timestamps
- Module-specific loggers
"""

import logging
import sys
from pathlib import Path
from typing import Optional

_loggers: dict = {}
_initialized: bool = False


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_to_console: bool = True,
    log_format: Optional[str] = None,
    use_colors: bool = True,
) -> None:
    """
    Configure global logging settings.

    Args:
        log_level: Minimum log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Path to log file (None = no file output)
        log_to_console: Enable console output
        log_format: Custom log format string (None = use default)
        use_colors: Enable colored output in console
    """
    global _initialized

    level = getattr(logging, log_level.upper(), logging.INFO)

    if log_format is None:
        if use_colors and log_to_console:
            log_format = "\033[1;32m%(asctime)s\033[0m \033[1;36m%(levelname)-8s\033[0m \033[1;34m%(name)s\033[0m: %(message)s"
        else:
            log_format = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"

    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(log_format, datefmt=date_format)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance by name.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        Logger instance
    """
    global _loggers

    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    _loggers[name] = logger

    return logger


def debug(msg: str, logger_name: str = "booklet-ocr") -> None:
    """Log a debug message."""
    get_logger(logger_name).debug(msg)


def info(msg: str, logger_name: str = "booklet-ocr") -> None:
    """Log an info message."""
    get_logger(logger_name).info(msg)


def warning(msg: str, logger_name: str = "booklet-ocr") -> None:
    """Log a warning message."""
    get_logger(logger_name).warning(msg)


def error(msg: str, logger_name: str = "booklet-ocr") -> None:
    """Log an error message."""
    get_logger(logger_name).error(msg)


def critical(msg: str, logger_name: str = "booklet-ocr") -> None:
    """Log a critical message."""
    get_logger(logger_name).critical(msg)


def print_like(msg: str, logger_name: str = "booklet-ocr", level: str = "INFO") -> None:
    """
    Print-like function that logs instead of printing.

    Used for gradual migration from print to logging.

    Args:
        msg: Message to log
        logger_name: Logger name
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    logger = get_logger(logger_name)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, msg)
